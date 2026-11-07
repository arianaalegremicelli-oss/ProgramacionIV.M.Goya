# Ejercicios Resueltos - Clase 8
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Seguridad en APIs: OWASP Top 10, Rate Limiting (Throttling), CORS, Sanitización y Auditoría

---

## 1. Mitigación del OWASP Top 10 en TaskFlow

- **Control de Acceso e Inyección:**
  - BOLA / IDOR prevenido en todas las vistas mediante aislamiento en `get_queryset` y comprobación de permisos por rol (`IsProjectAdminOrReadOnly`).
  - Inyección SQL prevenida mediante el uso exclusivo de consultas parametrizadas del ORM de Django.
- **Prevención de Ataques de Fuerza Bruta (Rate Limiting):**
  - Implementación de `LoginRateThrottle` en `core/throttles.py` restringiendo el endpoint de obtención de token a un máximo de 5 peticiones por minuto por dirección IP.
  - Tasas globales en `REST_FRAMEWORK`: anónimos (`20/minute`) y usuarios autenticados (`100/minute`).
- **Prevención de Cross-Site Scripting (XSS):**
  - Sanitización en `TaskSerializer.validate_description` con la librería `nh3`, eliminando cualquier inyección de etiquetas HTML/scripts en el cuerpo de las tareas.

---

## 2. Configuración de CORS y Logging de Auditoría

- **CORS (`django-cors-headers`):**
  - Middleware ubicado al inicio de la cadena en `settings.py`.
  - Lista blanca estricta mediante `CORS_ALLOWED_ORIGINS` restringida a los dominios autorizados de desarrollo y producción.
- **Auditoría y Registro de Incidentes (`SecurityLog`):**
  - Modelo `SecurityLog` (`core/models.py`) para trazabilidad de eventos sensibles.
  - Registro automático de intentos fallidos de autenticación en `ThrottledTokenObtainPairView` y de accesos no autorizados en `IsProjectAdminOrReadOnly`.

---

## 3. Respuestas a Preguntas de Repaso

### 1. Las tres preguntas de un Modelo de Amenazas
1. **¿Qué tenemos que proteger? (Activos):** Cuentas de usuario, datos de proyectos/tareas confidenciales, credenciales del sistema (`SECRET_KEY`).
2. **¿Por dónde pueden ingresar? (Superficie de ataque):** Endpoints HTTP públicos, formularios de entrada, cabeceras HTTP, dependencias de terceros.
3. **¿Quiénes y cómo pueden atacar? (Vectores de amenaza):** Bots automatizados de fuerza bruta, usuarios legítimos manipulando IDs numéricos (IDOR), atacantes ejecutando scripts en clientes vulnerables (XSS).

### 2. Principio de Defensa en Profundidad y capas en TaskFlow
Establece que la seguridad no debe depender de una única barrera. Si un control es eludido, las capas subsiguientes deben mitigar el ataque:
`HTTPS / Red -> CORS -> Rate Limiting -> JWT (Autenticación) -> Permisos / QuerySet -> Sanitización nh3 -> ORM Parametrizado -> Restricciones BD -> Auditoría (Logs)`.

### 3. ¿Por qué el ORM protege de SQL Injection y cómo se vulnera?
El ORM separa estrictamente el código SQL del dato suministrado por el usuario mediante consultas parametrizadas (placeholders). Se vulneraría si se concatenan cadenas sin sanear dentro de consultas crudas (`cursor.execute(f"SELECT ... WHERE id = '{user_input}'")`).

### 4. Ataques de autenticación y mitigación mediante Rate Limiting
- **Fuerza Bruta:** Probar un diccionario de claves contra una cuenta conocida.
- **Credential Stuffing:** Emplear listas masivas de credenciales filtradas de otras plataformas.
- **Denegación de Servicio (DoS):** Saturar la base de datos provocando miles de cálculos de hashing por segundo.
*Mitigación:* Limitar la frecuencia a 5 intentos por minuto por IP frena a los bots automatizados y vuelve inútil el ataque.

### 5. Algoritmo de DRF para Rate Limiting
Utiliza una ventana de tiempo deslizante en caché. Registra las marcas temporales de cada petición por clave identificadora (IP o ID de usuario). Si se supera la cuota permitida, responde con **HTTP 429 Too Many Requests** junto con la cabecera `Retry-After: <segundos>`.

### 6. ¿Por qué limitar el ritmo en lugar de bloquear la cuenta tras 5 fallos?
Bloquear la cuenta permitiría a un atacante ejecutar una denegación de servicio dirigida: con solo fallar deliberadamente 5 intentos con el usuario del administrador de una empresa, dejaría fuera al titular legítimo. El límite por IP penaliza al host atacante sin privar del servicio al usuario legítimo.

### 7. Política del Mismo Origen (SOP)
Es una directiva de seguridad que impide que un script cargado desde un origen interactúe con recursos de otro origen diferente (determinado por el trío: protocolo + dominio + puerto).
- `http://a.com` y `https://a.com` son orígenes distintos (difiere el protocolo).
- `http://a.com:80` y `http://a.com` corresponden al mismo origen (el puerto 80 es el estándar HTTP).

### 8. Petición Previa (Preflight Request)
Es una solicitud previa realizada por el navegador mediante el método `OPTIONS` antes de ejecutar peticiones cross-origin no simples (que envíen JSON, cabeceras personalizadas como `Authorization`, etc.). Consulta al backend si el origen y las cabeceras están permitidos. Si la respuesta no incluye las cabeceras CORS esperadas, el navegador aborta la petición real.

### 9. Diferencia entre CORS y CSRF
- **CORS:** Mecanismo defensivo del navegador que restringe la lectura de respuestas entre distintos orígenes desde código JavaScript.
- **CSRF:** Ataque que induce al navegador a emitir peticiones no deseadas a un sitio autenticado aprovechando el envío automático de cookies de sesión. Las APIs basadas puramente en JWT no son vulnerables a CSRF porque el navegador no envía automáticamente la cabecera `Authorization: Bearer`.

### 10. Tres tipos de ataques XSS y sus tres defensas
- **XSS Almacenado:** El script malicioso se persiste en la base de datos y se ejecuta en los navegadores de cada usuario que visualiza el recurso.
- **XSS Reflejado:** El payload viaja en los parámetros de la URL y se renderiza en la respuesta inmediata.
- **XSS Basado en DOM:** La inyección ocurre en el frontend al manipular dinámicamente `innerHTML`.
*Defensas:*
1. **Validación:** Rechazar datos de entrada no conformes.
2. **Sanitización:** Limpiar cadenas con librerías seguras como `nh3` eliminando etiquetas no autorizadas.
3. **Escape Contextual:** Renderizar siempre texto codificando caracteres especiales (`<`, `>`, `&`).

### 11. ¿Qué registrar y qué omitir en los Logs de Auditoría?
- **Registrar:** Dirección IP, marca temporal, acción efectuada (login fallido, elevación de privilegios, modificación de proyectos sensibles) y usuario involucrado.
- **Omitir:** Contraseñas en texto plano (incluso las incorrectas), tokens JWT, números de tarjetas de crédito o secretos de integración.

### 12. ¿Qué hacer si se commitea una clave secreta a GitHub?
Eliminar la clave del código fuente en un commit posterior es insuficiente, ya que queda registrada en el historial permanente de Git. Es mandatario:
1. Revocar e invalidar inmediatamente la clave en el proveedor o en la configuración interna.
2. Generar un nuevo secreto criptográfico seguro y cargarlo mediante variables de entorno (`.env`).

### 13. Tres encabezados de seguridad HTTP
- `Strict-Transport-Security (HSTS)`: Obliga al navegador a comunicarse exclusivamente mediante HTTPS durante el período establecido.
- `X-Frame-Options: DENY`: Evita que el sitio sea embebido dentro de un iframe, neutralizando ataques de clickjacking.
- `Content-Security-Policy (CSP)`: Lista blanca estricta que define qué orígenes pueden ejecutar scripts, cargar fuentes o estilos.

---

## 4. Tarea para la Casa Resuelta

1. **Auditoría de Permisos Denegados en `IsProjectAdminOrReadOnly`:**
   - Si un usuario miembro intenta una operación de escritura (`POST`, `PUT`, `PATCH`, `DELETE`) en un proyecto donde no es administrador, se registra automáticamente en `SecurityLog` con `action="permission_denied"` y se emite un log de nivel WARNING.
   - **Pregunta teórica:** ¿Por qué un usuario no miembro nunca llega a este punto?  
     Porque la vista filtra el queryset en `get_queryset()` según las membresías del usuario (`project__memberships__user=request.user`). Para un no miembro, el proyecto o tarea no existe en su conjunto accesible, respondiendo inmediatamente con `404 Not Found` sin alcanzar la evaluación de `has_object_permission`.
2. **Diferencia entre `CORS_ALLOWED_ORIGINS` y `CORS_ALLOW_CREDENTIALS`:**
   - `CORS_ALLOWED_ORIGINS`: Define la lista blanca de dominios que pueden consumir la API mediante solicitudes CORS.
   - `CORS_ALLOW_CREDENTIALS`: Habilita al navegador a transmitir credenciales de transporte (cookies de sesión, cabeceras de autorización HTTP básicas o certificados cliente TLS) en peticiones cross-origin. Solo es requerida cuando el esquema de autenticación depende de cookies del navegador; en sistemas desacoplados con tokens JWT transmitidos vía cabecera `Authorization`, no se necesita activar para evitar riesgos de seguridad adicionales.
