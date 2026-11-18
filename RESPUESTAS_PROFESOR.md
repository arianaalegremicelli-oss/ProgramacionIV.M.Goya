# Ejercicios Resueltos - Clase 10
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Arquitectura Orientada a Eventos (EDA), Broadcast, Presencia y Escalabilidad con Redis

---

## 1. Implementación de Arquitectura Orientada a Eventos (EDA)

- **Redis como Channel Layer:**
  - Se configuró `channels_redis.core.RedisChannelLayer` en `config/settings.py` apuntando a `REDIS_URL`.
  - Permite desacoplar los procesos web de los consumers y escalar horizontalmente el backend.
- **Servicio de Notificaciones (`core/services.py`):**
  - `NotificationService._send`: ejecuta `group_send` encapsulado con `async_to_sync` sobre el grupo `project_{{project_id}}`.
  - Manejo de fallos con degradación elegante: si Redis no responde, se registra la excepción en log pero no se aborta la persistencia de la tarea.
  - Eventos emitidos:
    - `notify_task_created`: disparado en `TaskViewSet.perform_create`.
    - `notify_task_updated`: disparado en `TaskViewSet.perform_update`.
    - `notify_task_completed`: disparado en `TaskViewSet.complete`.

---

## 2. Seguridad en WebSockets y Sistema de Presencia

- **Autenticación con JWT (`core/ws_auth.py`):**
  - Implementación de `JWTAuthMiddleware` que intercepta `?token=<access>` de la query string y valida criptográficamente el token con `AccessToken(token)`.
- **Consumer Completo (`core/consumers.py`):**
  - Validación de membresía del usuario sobre el proyecto antes de aceptar el handshake (`MembershipService.is_member`).
  - Notificaciones de presencia automáticas: emisión de evento `presence_update` con estado `online` al conectar y `offline` al desconectar.
  - Manejo de desconexión segura comprobando `self.joined` para evitar notificaciones de usuarios que fueron rechazados en el handshake.

---

## 3. Respuestas a Preguntas de Repaso

### 1. Comando vs. Evento
- **Comando:** Intención dirigida a un receptor específico que pide ejecutar una acción antes de que ocurra (puede fallar o ser rechazada).  
  *Ejemplo en TaskFlow:* `POST /api/tasks/` ("Crear esta tarea").
- **Evento:** Hecho inmutable que informa algo que ya ocurrió exitosamente; se emite en tiempo pasado y no tiene destinatario único.  
  *Ejemplo en TaskFlow:* `task_created` ("La tarea #5 fue creada").

### 2. Publicar/Suscribir (Pub/Sub) vs. Cola de Mensajes (Queue)
- **Pub/Sub (Tópico / Grupo):** Un productor publica un mensaje y todos los consumidores suscriptos reciben una copia (difusión 1 a N). Si no hay nadie escuchando en ese instante, el mensaje no se retiene.
- **Cola de Mensajes:** Un mensaje se encola y es procesado por un único consumidor trabajador (1 a 1). El mensaje permanece persistido hasta ser consumido o confirmado (*ack*).

### 3. Garantía de entrega del Channel Layer y consecuencias en el cliente
Channels ofrece garantía **at-most-once** (a lo sumo una vez): el mensaje se transmite por el socket pero no se garantiza persistencia ni reintento si la red cae. Por eso, el cliente frontend debe considerar los eventos como avisos para invalidar su caché y resincronizar el estado mediante una petición REST normal.

### 4. ¿Qué es la consistencia eventual?
Es el modelo donde los distintos nodos o clientes del sistema alcanzan el mismo estado después de un breve lapso de tiempo, y no necesariamente de forma atómica instantánea. En TaskFlow, la base de datos se actualiza primero y las pantallas de otros usuarios reflejan el cambio milisegundos después al recibir el evento.

### 5. Comparativa: Redis Pub/Sub vs. RabbitMQ vs. Kafka
- **Redis Pub/Sub:** Broker ultraliviano en memoria; no persiste mensajes ni gestiona acuses de recibo. Ideal para notificaciones instantáneas y WebSockets.
- **RabbitMQ:** Broker tradicional basado en el estándar AMQP con colas avanzadas, enrutamiento complejo, reintentos y confirmación de entrega (*acks*).
- **Apache Kafka:** Plataforma de registro de eventos distribuido (*event streaming*) particionado y persistido en disco de altísimo rendimiento para procesamiento de analítica y auditoría histórica.

### 6. Escalado Vertical vs. Horizontal e incompatibilidad de `InMemoryChannelLayer`
- **Vertical:** Incrementar CPU y RAM del mismo servidor.
- **Horizontal:** Añadir múltiples réplicas del servidor detrás de un balanceador de carga.
- `InMemoryChannelLayer` almacena los grupos en la memoria RAM del proceso local; si el usuario A está conectado al Servidor 1 y el usuario B al Servidor 2, los mensajes nunca se cruzan. Redis centraliza el pizarrón de grupos permitiendo escalar horizontalmente.

### 7. ¿Por qué el evento debe publicarse después de confirmar la transacción de base de datos?
Porque si se emite el evento antes del commit y la base de datos falla o revierte la transacción (*rollback*), los clientes WebSocket recibirán la notificación de una tarea que en realidad jamás existió en la base de datos.

### 8. WebSockets, CORS y Cross-Site WebSocket Hijacking (CSWSH)
La Política del Mismo Origen (SOP) no restringe el handshake de WebSockets. Un sitio malicioso en otro dominio podría abrir una conexión WebSocket contra nuestra API. Si nos autenticáramos por cookies de sesión automáticas, el atacante obtendría acceso a las notificaciones privadas del usuario. En TaskFlow nos protegemos requiriendo el token JWT explícito en el parámetro de consulta (`?token=`), valor que el sitio atacante no puede deducir ni obtener.

### 9. Casos complejos en sistemas de presencia y sus soluciones
1. **Múltiples pestañas/dispositivos:** Un usuario con dos ventanas abiertas marcaría "offline" al cerrar solo una. *Solución:* Mantener un contador o conjunto de conexiones activas en Redis por usuario y solo emitir "offline" cuando el recuento llegue a cero.
2. **Cortes de red imprevistos:** Si un cliente pierde internet sin emitir el frame de cierre TCP. *Solución:* Emplear latidos (*heartbeats*) de ping/pong periódicos; si expira el tiempo de espera (*timeout*), el servidor asume la desconexión.

### 10. Estrategia de reconexión: Backoff, Jitter y Resincronización
- **Backoff Exponencial:** Incrementar progresivamente el tiempo de espera entre intentos fallidos (1s, 2s, 4s, 8s...) para evitar saturar al backend caído.
- **Jitter (Azar):** Agregar una variación aleatoria al intervalo de espera para desfasar los intentos de cientos de clientes simultáneos evitando tormentas de conexiones (*thundering herd*).
- **Resincronización:** Al restablecer el socket, solicitar el estado actual por REST para recuperar cualquier evento emitido durante el periodo de desconexión.

---

## 4. Tarea para la Casa Resuelta

1. **Eventos `task_updated` y `task_completed`:**
   - Incorporados en `NotificationService` reutilizando el método base `_send`.
   - `notify_task_updated(task)` conectado a `TaskViewSet.perform_update`.
   - `notify_task_completed(task)` conectado a la acción `@action complete` de `TaskViewSet`.
2. **Respuesta Teórica: Redis vs. Kafka (Pregunta 3):**
   - Para las notificaciones en vivo de TaskFlow, **Redis** es la herramienta ideal debido a su mínima latencia en memoria y simplicidad de configuración.
   - **Kafka** sería desproporcionado porque retiene un historial persistente de eventos que no necesitamos; solo requerimos que quienes estén conectados en ese instante reciban el aviso. Kafka conviene cuando los eventos deben guardarse para analítica masiva o reprocesamiento posterior.
