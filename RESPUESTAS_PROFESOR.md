# Ejercicios Resueltos - Clase 9
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Tiempo Real con Django Channels, WebSockets y Servidores Asincrónicos ASGI

---

## 1. Migración Arquitectónica a ASGI y Django Channels

- **Configuración de Daphne y ASGI (`config/settings.py` y `config/asgi.py`):**
  - Registro de `"daphne"` como primera entrada en `INSTALLED_APPS` para delegar la atención del servidor de desarrollo a un entorno asincrónico.
  - Implementación de `config/asgi.py` utilizando `ProtocolTypeRouter`:
    - Rama HTTP delegada en `get_asgi_application()`.
    - Rama WebSocket encapsulada en `AuthMiddlewareStack(URLRouter(core.routing.websocket_urlpatterns))`.
  - Configuración inicial del Channel Layer mediante `InMemoryChannelLayer`.

---

## 2. Implementación de Consumers y Enrutamiento en Tiempo Real

- **Consumer Asincrónico (`core/consumers.py`):**
  - Creación de `TaskNotificationConsumer` heredando de `AsyncWebsocketConsumer`.
  - Gestión del ciclo de vida de conexión: `connect`, `disconnect`, `receive` y `task_notification`.
  - Integración a grupos dinámicos por proyecto (`project_{{project_id}}`).
- **Enrutamiento WebSocket (`core/routing.py`):**
  - Definición de patrón regex: `r"ws/projects/(?P<project_id>\d+)/$"`.

---

## 3. Respuestas a Preguntas de Repaso

### 1. Comparativa de técnicas de tiempo real en la web
| Técnica | Quién inicia | Dirección | Naturaleza de la conexión | Latencia | Sobrecarga |
|---|---|---|---|---|---|
| **Polling** | Cliente a intervalos fijos | Cliente -> Servidor | Petición HTTP nueva cada vez | Alta (hasta N segundos) | Máxima (cabeceras completas por petición) |
| **Long-Polling** | Cliente (el servidor demora la respuesta) | Cliente -> Servidor | Conexión HTTP retenida temporalmente | Moderada | Alta (reapertura constante de peticiones) |
| **Server-Sent Events (SSE)** | Servidor sobre conexión abierta | Servidor -> Cliente (Unidireccional) | Conexión HTTP persistente | Mínima | Baja |
| **WebSockets** | Ambos indistintamente | Bidireccional | Conexión TCP persistente dúplex | Mínima | Mínima (frames ligeros sin headers HTTP) |

### 2. El Handshake de WebSocket y el código HTTP 101
El cliente realiza una petición HTTP `GET` estándar solicitando la actualización mediante cabeceras `Upgrade: websocket` y `Connection: Upgrade` acompañadas de un nonce aleatorio `Sec-WebSocket-Key`. El servidor acepta respondiendo **HTTP 101 Switching Protocols** y calculando la firma `Sec-WebSocket-Accept`. A partir de ese momento, la conexión TCP subyacente deja de ser HTTP y pasa a comunicarse en tramas (*frames*) WebSocket bidireccionales.

### 3. ¿Por qué es posible autenticar al usuario durante el Handshake?
Dado que el handshake inicial es una petición HTTP regular, viaja transportando las cookies del navegador, encabezados estándar y atravesando los middlewares tradicionales. `AuthMiddlewareStack` inspecciona las credenciales durante esta etapa inicial y puebla el diccionario `scope["user"]`.

### 4. Tramas (Frames), Ping/Pong y Código de Cierre 1006
- **Frame:** Unidad atómica binaria o de texto en la que viaja la información sobre la conexión WebSocket sin cabeceras redundantes.
- **Ping / Pong:** Tramas de control periódicas para verificar que la conexión continúe abierta y activa a nivel de red (*heartbeat*).
- **Código 1006:** Código reservado que indica que la conexión se cerró abruptamente por una falla imprevista de red sin haber ejecutado el intercambio formal de cierre.

### 5. Implicancias de conexiones que duran horas en el servidor
- **Consumo persistente de memoria:** Cada conexión activa consume recursos del sistema de forma ininterrumpida.
- **Gestión de concurrencia:** El servidor debe coordinar miles de conexiones concurrentes en reposo mediante arquitecturas asincrónicas no bloqueantes.
- **Infraestructura de mensajería (Backplane):** Se requiere un mecanismo compartido (Channel Layer / Redis) para comunicar eventos originados en un proceso hacia conexiones abiertas en otros procesos o servidores.
- **Tolerancia a desconexiones:** El cliente frontend debe implementar lógica de reconexión automática con retroceso exponencial (*exponential backoff*).

### 6. WSGI vs. ASGI y limitaciones de `runserver` clásico
- **WSGI:** Modelo sincrónico bloqueante diseñado para el paradigma tradicional donde un proceso atiende una petición HTTP de corta duración y devuelve la respuesta.
- **ASGI:** Especificación estándar asincrónica que maneja múltiples protocolos simultáneos (HTTP, WebSockets) manteniendo conexiones concurrentes abiertas a largo plazo. El comando `runserver` estándar de Django es WSGI; por ello se instala Daphne para reemplazar el servidor de desarrollo por uno ASGI.

### 7. ¿Qué es el Bucle de Eventos (Event Loop)?
Es un mecanismo de concurrencia que ejecuta tareas en un único hilo, alternando de manera cooperativa entre operaciones cada vez que una tarea queda esperando una respuesta de Entrada/Salida (lectura de socket de red o base de datos), permitiendo que miles de conexiones en espera sean gestionadas eficientemente sin agotar los hilos del sistema operativo.

### 8. Principio de "No Bloquear el Bucle de Eventos" y `database_sync_to_async`
Si se ejecuta una función bloqueante dentro del bucle asincrónico (como las consultas al ORM de Django, que es sincrónico), todo el bucle se detiene congelando la atención de todas las conexiones simultáneas del worker. La utilidad `database_sync_to_async` traslada la ejecución de la consulta a un hilo secundario liberando inmediatamente el bucle principal.

### 9. Ciclo de vida de un Consumer en Django Channels
1. `connect()`: Se establece el handshake; el consumer decide si acepta la conexión (`self.accept()`), rechaza (`self.close()`) y suscribe la sesión a grupos.
2. `receive()`: Se activa cada vez que el cliente transmite un mensaje.
3. Métodos receptores de grupo: Invocados cuando un evento es emitido hacia el grupo del channel layer.
4. `disconnect()`: Invocado al cerrarse el socket; desafilia al canal de los grupos y limpia recursos.

### 10. Concepto de Grupo / Sala en diferentes tecnologías
Es un canal de comunicación agrupado donde un mensaje emitido es retransmitido en broadcast a todos los sockets suscritos.
- **Django Channels:** Grupo (*Group*).
- **Socket.IO:** Sala (*Room*).
- **SignalR (.NET):** Grupo (*Group* / *Hub*).

---

## 4. Tarea para la Casa Resuelta

1. **Rechazo de conexión si el proyecto no existe:**
   - Implementado en `TaskNotificationConsumer.connect`:
     ```python
     existe = await self._project_exists()
     if not existe:
         await self.close()
         return
     ```
   - La comprobación `_project_exists` se ejecuta de forma no bloqueante mediante el decorador `@database_sync_to_async`, consultando `Project.objects.filter(id=self.project_id).exists()`.
   - Si el `project_id` provisto en la URL no existe en la base de datos, el servidor cierra inmediatamente la conexión mediante `self.close()` impidiendo la suscripción al grupo.
