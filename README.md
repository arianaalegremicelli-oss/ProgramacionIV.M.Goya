# Ejercicios Resueltos - Clase 7
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Roles, Permisos por Recurso, Transacciones ACID y Autenticación Federada (OAuth / OpenID Connect)

---

## 1. Modelo de Membresías y Roles por Proyecto

- **Modelo `ProjectMembership` (`core/models.py`):**
  - Tabla intermedia que vincula `User` y `Project` con roles: `admin` y `miembro`.
  - Restricción de unicidad a nivel base de datos: `unique_together = ("project", "user")`.
- **Transacción Atómica en Creación de Proyectos:**
  - En `ProjectViewSet.perform_create`, la creación del proyecto y la asignación del usuario creador como `admin` se ejecutan dentro de `with transaction.atomic()`, garantizando las propiedades ACID.
- **Servicio de Membresías (`core/services.py`):**
  - Métodos encapsulados: `is_member`, `is_admin` y `projects_for(user)`.

---

## 2. Permisos por Recurso y Aislamiento Multitenant

- **Permiso Personalizado (`core/permissions.py`):**
  - Implementación de `IsProjectAdminOrReadOnly`:
    - Métodos seguros (`SAFE_METHODS`: GET, HEAD, OPTIONS) permitidos a cualquier miembro del proyecto.
    - Métodos de modificación (`POST`, `PUT`, `PATCH`, `DELETE`) restringidos exclusivamente a administradores del proyecto.
- **Protección de la Creación de Tareas:**
  - Validación explícita en `perform_create` y `perform_update` de `TaskViewSet` verificando rol de administrador sobre el proyecto de destino mediante `check_project_admin`.

---

## 3. Respuestas a Preguntas de Repaso

### 1. ¿Qué es una matriz de permisos y por qué se construye antes de programar?
Es una tabla cruzada que mapea recursos y operaciones (filas) con los roles existentes (columnas) definiendo si la acción está permitida o prohibida. Se diseña de forma previa al desarrollo para definir las reglas de negocio con claridad, evitar inconsistencias arquitectónicas y servir como guía directa para los casos de prueba unitarios.

### 2. Cuatro modelos de autorización
- **Por Propiedad:** El acceso depende exclusivamente de ser el creador/dueño del objeto (modelo de la Clase 6 con `owner`).
- **Listas de Control de Acceso (ACL):** Cada recurso individual mantiene una lista granular de usuarios y permisos (ej. Google Drive).
- **Control de Acceso Basado en Roles (RBAC):** Los permisos se asocian a roles y los usuarios adquieren roles dentro de un contexto (modelo adoptado en TaskFlow con roles `admin` y `miembro` por proyecto).
- **Basado en Atributos (ABAC):** Evalúa atributos del usuario, del recurso y del entorno (ej. hora del día, dirección IP, departamento).

### 3. Concepto de Sistema Multi-inquilino (Multitenant)
Arquitectura donde una sola instancia de software sirve a múltiples organizaciones o espacios aislados (inquilinos). En TaskFlow, cada `Project` constituye un espacio aislado donde los usuarios no pueden ver ni modificar recursos pertenecientes a proyectos en los que no participan.

### 4. ¿Por qué el sistema de permisos nativo de Django no alcanza para TaskFlow?
Los permisos nativos de Django son globales a nivel de modelo (ej. permiso general para editar *todas* las tareas). En TaskFlow, un usuario puede ser administrador con privilegios totales en el Proyecto A, pero ser un simple miembro de solo lectura en el Proyecto B. Se requiere un modelo de roles contextual por recurso (`ProjectMembership`).

### 5. ¿Por qué la regla "no ser miembro dos veces" debe residir en la base de datos?
Porque dos peticiones concurrentes podrían pasar la validación en Python simultáneamente antes de que alguna guarde el registro (condición de carrera). `unique_together` delega la restricción en un índice único del motor de base de datos como última línea de defensa infranqueable.

### 6. Las dos capas de control de acceso en DRF
1. **Filtrado de QuerySet (`get_queryset`):** Control de visibilidad. Si el recurso no pertenece al usuario, no aparece y devuelve `404 Not Found`.
2. **Clases de Permiso (`permission_classes` y `has_object_permission`):** Control de operación. Si el recurso existe y es visible pero el usuario carece del rol necesario para la acción, devuelve `403 Forbidden`.

### 7. ¿Por qué `has_object_permission` no protege la creación (`POST`)?
Porque durante una petición de creación (`POST`) el objeto todavía no fue instanciado ni persistido, por lo que DRF nunca invoca `has_object_permission`. La protección de la creación debe realizarse evaluando los datos validados en el método `perform_create` de la vista.

### 8. ¿Qué significa que una operación sea atómica? Relación con ACID
Significa que un conjunto de operaciones se ejecuta como una unidad indivisible: o se aplican todas exitosamente o, ante cualquier fallo, se revierte todo (*rollback*) dejando la base intacta. Cumple con:
- **A (Atomicidad):** Se crea el proyecto y la membresía, o nada.
- **C (Consistencia):** No quedan proyectos huérfanos sin administrador.
- **I (Aislamiento):** Transacciones intermedias no son visibles por otros procesos.
- **D (Durabilidad):** Al confirmarse, los datos persisten de manera definitiva.

### 9. ¿Qué problema resolvió OAuth frente al modelo anterior?
Antes de OAuth, para que una aplicación externa accediera a datos de un proveedor, el usuario debía entregarle directamente su usuario y contraseña, otorgando acceso ilimitado e irrevocable. OAuth resolvió esto delegando la autorización mediante tokens con permisos limitados (*scopes*) y revocables, sin compartir jamás las credenciales.

### 10. Diferencia entre OAuth 2.0 y OpenID Connect (OIDC)
- **OAuth 2.0:** Es un protocolo de **autorización** (acceso a recursos y APIs delegadas).
- **OpenID Connect (OIDC):** Es una capa construida sobre OAuth 2.0 dedicada a la **autenticación** (identidad federada), introduciendo el estándar del `ID Token` (un JWT con la identidad verificada del usuario).

### 11. Ventajas de seguridad del flujo Authorization Code
El token no viaja por el navegador. El usuario autoriza y el proveedor devuelve un código temporal de un solo uso. La aplicación intercambia ese código directamente de servidor a servidor enviando su `client_secret`. Ni los tokens ni el secreto quedan expuestos al frontend o al historial del navegador.

---

## 4. Tarea para la Casa Resuelta

1. **Acción `add_member` en `ProjectViewSet`:**
   - Endpoint: `POST /api/projects/<id>/add_member/` con body `{"username": "...", "role": "miembro"}`.
   - Protegida por `IsProjectAdminOrReadOnly`: únicamente los administradores del proyecto pueden invocarla.
   - Respuestas HTTP validadas:
     - `404 Not Found` si el usuario no existe.
     - `400 Bad Request` si el usuario ya forma parte del proyecto.
     - `201 Created` con los datos de la nueva membresía.
2. **Diagrama de Flujo Completo OAuth (Authorization Code):**
   ```
   1. [Navegador] El usuario hace clic en "Iniciar sesión con Google".
   2. [Navegador -> TaskFlow] GET /accounts/google/login/
   3. [TaskFlow -> Navegador] Redirección 302 a Google con client_id, redirect_uri, scope y state.
   4. [Navegador -> Google] El usuario inicia sesión y aprueba los consentimientos.
   5. [Google -> Navegador] Redirección a la redirect_uri de TaskFlow incluyendo ?code=...&state=...
   6. [Navegador -> TaskFlow] Envía el código de autorización temporal (un solo uso).
   7. [TaskFlow -> Google (Servidor a Servidor)] Envía POST con code + client_secret.
   8. [Google -> TaskFlow (Servidor a Servidor)] Responde con Access Token e ID Token (JWT).
   9. [TaskFlow -> Navegador] Sesión creada; redirige a /api/auth/social/jwt/ entregando par JWT.
   ```
   - **En el Navegador:** Pasos 1, 2, 3, 4, 5, 6 y 9.
   - **Servidor a Servidor (Privado y Seguro):** Pasos 7 y 8 (el `client_secret` jamás se expone).
