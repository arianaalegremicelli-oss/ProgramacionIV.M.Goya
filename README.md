# Ejercicios Resueltos - Clase 6
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Autenticación con JWT (JSON Web Tokens), SimpleJWT, Registro de Usuarios y Propietario de Tareas

---

## 1. Implementación de Autenticación Stateless con JWT

- **Configuración de SimpleJWT (`config/settings.py`):**
  - Se configuró `JWTAuthentication` como clase primaria en `DEFAULT_AUTHENTICATION_CLASSES`.
  - Política de seguridad por defecto: `DEFAULT_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]`.
  - Configuración de tokens: `ACCESS_TOKEN_LIFETIME` en 30 minutos, `REFRESH_TOKEN_LIFETIME` en 7 días y `ROTATE_REFRESH_TOKENS = True`.
- **Rutas de Autenticación (`config/urls.py`):**
  - `POST /api/token/`: emisión de par de tokens (Access y Refresh).
  - `POST /api/token/refresh/`: rotación y renovación del Access token.
  - `POST /api/register/`: registro público de nuevos usuarios vía `RegisterView`.

---

## 2. Registro y Modelo de Dominio con Propietario

- **Serializador de Registro (`core/serializers_auth.py`):**
  - Implementación de `RegisterSerializer` con hashing seguro mediante `User.objects.create_user`.
  - Contraseña de solo escritura (`write_only=True`) y validación de unicidad de email insensible a mayúsculas.
- **Relación de Tareas con Usuario (`core/models.py` y `core/views.py`):**
  - Agregado campo `owner` como Foreign Key hacia `AUTH_USER_MODEL` en el modelo `Task`.
  - `TaskViewSet.get_queryset()`: restringe el listado y operaciones estrictamente a `owner=request.user`.
  - `TaskViewSet.perform_create()`: asigna automáticamente el usuario autenticado como dueño.

---

## 3. Respuestas a Preguntas de Repaso

### 1. Autenticación vs. Autorización
- **Autenticación (401 Unauthorized):** Verifica la identidad del cliente (¿quién sos?). Si no hay credenciales válidas o el token expiró, la API responde 401.
- **Autorización (403 Forbidden):** Verifica los permisos sobre el recurso (¿tenés derecho a realizar esta acción?). La identidad es conocida pero no cuenta con privilegios suficientes.

### 2. Autenticación por Sesión vs. por JWT
| Criterio | Sesión (Stateful) | JWT (Stateless) |
|---|---|---|
| Almacenamiento en Servidor | Tabla de sesiones en base o Redis | Nada (solo la clave pública/privada de firma) |
| Transporte | Cookies gestionadas por el navegador | Header `Authorization: Bearer <token>` |
| Escalabilidad Horizontal | Requiere base compartida o sticky sessions | Alta: cualquier nodo valida la firma criptográfica |
| Revocación | Inmediata (se borra el registro de sesión) | Compleja (se requiere lista negra hasta expiración) |

### 3. Las tres partes de un JWT y su funcionamiento
Un JWT tiene la estructura `header.payload.signature`:
- **Header:** Algoritmo de firma y tipo de token en Base64URL.
- **Payload:** Reclamaciones o claims (`user_id`, `exp`, etc.) en Base64URL.
- **Signature:** Hash HMAC-SHA256 del header + payload combinado con la `SECRET_KEY` del backend. Evita la alteración o falsificación de los datos.

### 4. ¿Qué ocurre si un atacante obtiene la `SECRET_KEY`?
Podría firmar tokens arbitrarios con cualquier `user_id` o permisos de superusuario, comprometiendo por completo la seguridad del sistema. Por este motivo se lee desde variables de entorno y se excluye de Git.

### 5. ¿Por qué se utilizan dos tokens (Access y Refresh)?
Para equilibrar seguridad y usabilidad. El **Access token** viaja continuamente y tiene una vida útil corta (30 minutos) para acotar la ventana de riesgo si es interceptado. El **Refresh token** tiene vida útil larga (7 días), se envía únicamente al endpoint de renovación y admite rotación automática para detectar y neutralizar reutilizaciones no autorizadas.

### 6. Almacenamiento del token en clientes Frontend
- **En memoria:** Máxima seguridad contra ataques XSS, pero se pierde la sesión al recargar la pestaña.
- **localStorage / sessionStorage:** Persiste ante recargas, pero es vulnerable a robo mediante inyección de scripts maliciosos (XSS).
- **Cookie HttpOnly con SameSite:** JavaScript no puede leer la cookie, mitigando XSS, pero reintroduce la necesidad de protección contra CSRF.

### 7. Diferencia entre Codificar, Cifrar y Hashear
- **Codificar (ej. Base64):** Conversión reversible sin clave para compatibilidad de transporte.
- **Cifrar (ej. AES):** Transformación reversible mediante una clave criptográfica para garantizar confidencialidad.
- **Hashear (ej. PBKDF2/SHA256):** Función unidireccional no reversible con sal e iteraciones, usada para validar contraseñas sin guardarlas en texto plano.

### 8. Importancia de la Sal y el Número de Iteraciones
- **Sal:** Secuencia aleatoria única por usuario que evita que dos usuarios con la misma contraseña tengan el mismo hash y anula el uso de tablas precalculadas (Rainbow Tables).
- **Iteraciones:** Ralentizan computacionalmente el cálculo del hash, haciendo inviables los ataques por fuerza bruta masiva en hardware de GPU.

### 9. Pipeline de evaluación en DRF y orden de autenticación
DRF ejecuta en orden:
1. `DEFAULT_AUTHENTICATION_CLASSES`: la primera clase que reconoce las credenciales puebla `request.user` y `request.auth`. Al colocar `JWTAuthentication` al inicio, los rechazos de token devuelven el encabezado estandarizado `WWW-Authenticate: Bearer`.
2. `DEFAULT_PERMISSION_CLASSES`: se evalúa `has_permission`. Si el usuario no está autenticado, responde 401; si está autenticado pero no tiene privilegios, responde 403.
3. Vista del recurso.

### 10. Principio de "Seguro por Defecto"
Configurar `IsAuthenticated` globalmente cierra todos los endpoints de la API por defecto. Solo los endpoints de registro, login y documentación pública se abren de forma explícita mediante `permission_classes = [AllowAny]`, previniendo descuidos de endpoints expuestos.

### 11. Vulnerabilidad IDOR y su prevención
IDOR (*Insecure Direct Object Reference*) ocurre cuando un cliente altera un parámetro identificador en la URL (por ejemplo, cambiar `/api/tasks/5/` a `/api/tasks/6/`) para acceder a información ajena. En TaskFlow se previene filtrando `get_queryset()` con `owner=self.request.user`, provocando que las tareas ajenas directamente no existan para ese usuario y respondan con un seguro 404 Not Found.

---

## 4. Tarea para la Casa Resuelta

1. **Flujo completo de expiración y renovación:**
   - Registro exitoso en `/api/register/` con código 201 Created.
   - Login en `/api/token/` obteniendo `access` y `refresh`.
   - Tras expirar el tiempo de vida (probado temporalmente con 30 segundos), la petición devuelve 401 Unauthorized.
   - Se renovó el token mediante `POST /api/token/refresh/` con `{"refresh": "<token>"}`, obteniendo un nuevo token de acceso válido sin exigir reingreso de credenciales.
2. **Revocación de Tokens y Token Blacklist:**
   - Si un atacante sustrae un Refresh token, podría obtener tokens de acceso hasta la expiración.
   - La librería `rest_framework_simplejwt.token_blacklist` soluciona esto persistiendo en base de datos los identificadores únicos (`jti`) de los refresh tokens rotados o revocados durante el logout, rechazando de inmediato cualquier reintento de uso.
3. **Análisis del endpoint `GET /api/projects/<id>/`:**
   - Al consultar un proyecto, el serializer anida todas las tareas vinculadas al proyecto globalmente, incluyendo tareas creadas por otros usuarios.
   - **Problema de seguridad detectado:** Falla de aislamiento entre inquilinos/usuarios en proyectos compartidos. Este problema se resuelve en la Clase 7 mediante el modelo de membresías por proyecto y roles específicos.
