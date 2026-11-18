# Ejercicios Resueltos - Clase 13 (Bonus)
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Frontend Mínimo (SPA en JavaScript Vanilla), Consumo de API REST, WebSockets y Manejo del DOM

---

## 1. Arquitectura Frontend Desacoplada (SPA Vanilla)

- **Estructura (`taskflow-frontend/`):**
  - `index.html`: interfaz semántica con secciones alternadas (`login-box` y `app-box`), controles accesibles y barra de paginación.
  - `app.js`: lógica en JavaScript asincrónico nativo (`async`/`await` y `fetch`), sin frameworks ni dependencias externas.
- **Flujos Implementados:**
  - Login contra `/api/token/` con persistencia en `sessionStorage`.
  - Carga dinámica de proyectos en elemento `<select>` respetando membresías.
  - Renderizado dinámico de tareas con paginación (`Anterior` / `Siguiente`).
  - Creación de tareas con propagación de errores del backend y sanitización mediante `textContent`.
  - Conexión reactiva por WebSocket que refresca la lista en vivo ante eventos `task_created` o `task_updated`.

---

## 2. Respuestas a Preguntas de Repaso

### 1. Ventajas de separar Frontend de Backend y otros consumidores de la API
- **Ventajas:**
  - Desacoplamiento total de tecnologías: el backend evoluciona sin rehacer el cliente.
  - Reutilización de la misma lógica de negocio y seguridad para múltiples interfaces.
  - Escalabilidad independiente de los servidores de interfaz frente a los servidores de datos.
- **Otros consumidores:** Aplicaciones móviles nativas (Android/iOS), integraciones de microservicios externos (como la comisión de los jueves), clientes de consola CLI o herramientas automatizadas de Inteligencia Artificial.

### 2. Renderizado en Servidor (SSR) vs. Aplicación de Página Única (SPA)
- **SSR (Server-Side Rendering):** El servidor genera y ensambla el HTML completo con datos en cada petición antes de transmitirlo al navegador.
- **SPA (Single Page Application):** El navegador descarga un único archivo HTML esqueleto con JavaScript; luego el cliente manipula el DOM dinámicamente solicitando únicamente datos crudos (JSON) a la API REST.

### 3. ¿Por qué `fetch` es asincrónico? Relación con `async`/`await` de Python
El entorno de JavaScript en el navegador opera sobre un único hilo de ejecución (Event Loop). Si una petición HTTP fuera sincrónica bloqueante, la ventana del navegador se congelaría por completo impidiendo clics, desplazamientos o animaciones mientras espera la red. Funciona idéntico al bucle asincrónico de Daphne y `AsyncWebsocketConsumer` en Python (Clase 9): cede el control mientras aguarda operaciones de entrada/salida.

### 4. ¿Por qué se debe evaluar `response.ok` tras un `fetch`?
Porque la promesa de `fetch()` únicamente se rechaza ante errores de red a nivel de socket (servidor caído o bloqueo de CORS). Si el servidor responde con códigos de error HTTP de aplicación como **401 Unauthorized**, **403 Forbidden** o **500 Internal Server Error**, la promesa se resuelve con éxito. La propiedad `response.ok` (que evalúa si el código de estado está en el rango 200-299) es la única manera de detectar fallos lógicos.

### 5. ¿Qué es el DOM y por qué usar `textContent` en vez de `innerHTML`?
- **DOM (Document Object Model):** Estructura jerárquica de árbol en memoria que representa los elementos HTML de la página como objetos de JavaScript manipulables.
- **`textContent` vs `innerHTML`:** `innerHTML` interpreta e inserta las cadenas como código HTML, abriendo la puerta a vulnerabilidades críticas de Cross-Site Scripting (XSS) si el texto contiene etiquetas `<script>` o atributos `onload`. `textContent` asigna texto plano puro escapando cualquier carácter especial de forma segura.

### 6. ¿Por qué la página no funciona adecuadamente al abrirla con doble clic?
Al hacer doble clic, el navegador carga la página mediante el protocolo local `file://`. Esto provoca:
1. El navegador envía el origen especial `"null"`, el cual es bloqueado por las políticas de CORS del backend Django.
2. Restricciones estrictas de seguridad local del navegador impiden el funcionamiento normal de módulos y peticiones AJAX. Por ello se debe servir mediante un servidor HTTP local (como `python -m http.server 5500` o la extensión Live Server).

### 7. ¿Qué es un sitio estático y qué es una Red de Distribución de Contenido (CDN)?
- **Sitio Estático:** Conjunto de archivos preconstruidos (HTML, CSS, JS, imágenes) que el servidor entrega directamente al cliente sin requerir ejecución ni renderizado en tiempo real en el backend.
- **CDN (Content Delivery Network):** Red distribuida geográficamente de servidores réplica en todo el mundo que almacenan en caché los archivos estáticos y los entregan a los usuarios desde el centro de datos geográficamente más cercano, reduciendo drásticamente la latencia de carga.

---

## 3. Tarea Opcional Resuelta

- **Persistencia de Sesión:** `sessionStorage.setItem("taskflow_access_token", accessToken)` permite recargar la pestaña sin perder el inicio de sesión.
- **Botón "Salir":** Función `logout()` que limpia el token, cierra el socket y restaura la vista de login.
- **Paginación Dinámica:** Botones `Anterior` y `Siguiente` controlados por los enlaces `next` y `previous` provistos por DRF.
- **Tiempo Real con WebSocket:** Integración de `WebSocket` hacia `ws://127.0.0.1:8000/ws/projects/<id>/?token=<access>`, recargando la lista automáticamente ante el aviso de una nueva tarea creada por otro miembro del equipo.
