# Ejercicios Resueltos - Clase 11
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Capa GraphQL con Graphene-Django: Esquema, Types, Queries, Mutations y Autenticación JWT

---

## 1. Esquema GraphQL y Tipos de Dominio

- **Tipos de GraphQL (`core/schema.py`):**
  - `ProjectType`, `TaskType` y `TagType` basados en `DjangoObjectType`.
  - Configuración `convert_choices_to_enum = False` en `TaskType` para conservar las opciones en minúsculas en paridad con la API REST.
- **Consultas (Queries):**
  - `all_projects`: lista los proyectos a los que pertenece el usuario autenticado.
  - `task(id)`: recupera una tarea validando que pertenezca a los proyectos del usuario.
  - `tasks_by_status(status)`: filtra tareas según el estado en proyectos permitidos.
- **Mutaciones (Mutations):**
  - `CreateTask`: valida permisos de administrador y reglas de serialización (`TaskSerializer`), persistiendo con `owner=user` y notificando en tiempo real vía `NotificationService`.
  - `UpdateTaskStatus`: mutación implementada para la tarea que modifica el estado aplicando validación de rol de admin sobre el proyecto.

---

## 2. Endpoint Unificado e Integración JWT

- **Vista Personalizada (`core/graphql_views.py`):**
  - `JWTGraphQLView` hereda de `GraphQLView` y autentica manualmente el encabezado `Authorization: Bearer <token>` mediante `JWTAuthentication().authenticate(request)`.
  - Puebla `request.user` para que esté disponible en `info.context.user` dentro de cada resolver.
- **Ruta (`config/urls.py`):**
  - Endpoint expuesto en `path("graphql/", csrf_exempt(JWTGraphQLView.as_view(graphiql=True)))`.

---

## 3. Respuestas a Preguntas de Repaso

### 1. ¿Qué es el SDL? Significado de `[TaskType!]!`
- **SDL (Schema Definition Language):** Sintaxis formal para declarar la estructura de tipos, relaciones y operaciones disponibles en una API GraphQL.
- `[TaskType!]!`: Indica una lista que **no puede ser nula** (signo de exclamación exterior) y donde **ninguno de sus elementos puede ser nulo** (signo de exclamación interior). Siempre devolverá al menos una lista vacía `[]`.

### 2. Los tres tipos de operación en GraphQL
1. **Query:** Operación de lectura (análogo a `GET`).
2. **Mutation:** Operación de escritura o mutación de datos (análogo a `POST`, `PUT`, `DELETE`).
3. **Subscription:** Operación reactiva en tiempo real sobre WebSockets (vinculada directamente a la Unidad 4 de Django Channels).

### 3. ¿Por qué una respuesta GraphQL puede devolver `data` y `errors` juntos?
Porque GraphQL admite **resultados parciales**: si en una misma consulta se solicitan dos campos independientes y uno falla (por ejemplo, por falta de permisos), el motor resuelve el campo exitoso en `data` e incluye el detalle del fallo en el arreglo `errors`, respondiendo usualmente con código **HTTP 200 OK**.

### 4. Comparativa REST vs. GraphQL
| Característica | REST | GraphQL |
|---|---|---|
| **Caché HTTP** | Nativa y sencilla mediante URLs únicas y headers (`ETag`, `Cache-Control`) | Compleja a nivel HTTP (todas las consultas son `POST /graphql/`); requiere librerías cliente (Apollo InMemoryCache) |
| **Versionado** | Por URL o encabezado (`/api/v1/`, `/api/v2/`) | Esquema continuo evolutivo sin versiones; se deprecian campos individuales con `@deprecated` |
| **Manejo de Errores** | Basado en códigos de estado HTTP (400, 401, 403, 404, 500) | Código HTTP 200 casi siempre; los errores viajan estructurados en la clave `errors` del JSON |

### 5. Ejecución en árbol y argumentos de un resolver (`root` e `info.context`)
GraphQL procesa consultas resolviendo primero el nodo raíz y luego ejecutando recursivamente los campos anidados.
- `root`: Representa el objeto padre retornado por el nivel superior (en `tasks`, `root` es la instancia de `Project`).
- `info.context`: Es el contexto global compartido de la petición (en nuestro caso, el objeto `request` con el usuario autenticado).

### 6. Problema N+1 en GraphQL y mitigación
Ocurre cuando se solicita una lista de N proyectos y para cada uno se consultan sus tareas: se ejecuta 1 consulta para los proyectos y N consultas individuales para las tareas (N+1 queries a la base).
- En el análisis de 6 proyectos, sin optimización se disparan 7 consultas SQL; con `prefetch_related("tasks")` se resuelve en exactamente **2 consultas SQL**. En GraphQL avanzado se resuelve mediante el patrón **DataLoader**.

### 7. Convenciones para diseñar Mutations
1. Emplear verbos imperativos claros (`createTask`, `updateTaskStatus`, `deleteProject`).
2. Retornar el objeto creado o modificado junto con un indicador booleano (`ok: Boolean`) para actualizar la interfaz del cliente sin consultas extras.
3. Usar tipos de entrada (*InputTypes*) para agrupar múltiples argumentos.

### 8. Riesgos de seguridad propios de GraphQL y mitigación
- **Consultas Circulares / Profundidad Excesiva:** Un atacante puede anidar `project { tasks { project { tasks ... } } }` provocando denegación de servicio (DoS). *Mitigación:* Limitar la profundidad máxima (*max query depth*).
- **Consultas Masivas / Complejidad:** Solicitar miles de campos calculados. *Mitigación:* Análisis y límite de costo de consulta (*query cost analysis*).
- **Introspección Expuesta:** El cliente puede descargar el esquema entero con `__schema`. *Mitigación:* Desactivar la introspección y la interfaz GraphiQL en entornos de producción.

### 9. Integración de fuentes externas en un Resolver
Un resolver puede consumir cualquier fuente (base relacional, Redis o APIs REST externas). En TaskFlow, un campo `holidayStatus` dentro de `TaskType` puede invocar directamente `HolidayService.is_holiday(root.due_date)`, unificando datos internos y externos en una única respuesta.

### 10. Unir Esquemas (Schema Stitching) vs. Federación y rol del Gateway
- **Schema Stitching:** El gateway descarga los esquemas de múltiples microservicios y los combina programáticamente en un solo servidor monolítico.
- **Federación (Apollo Federation):** Cada microservicio es dueño de su propio subgrafo y define cómo extender tipos compartidos; un **Gateway** inteligente compone el supergrafo y distribuye la ejecución de las consultas hacia los servicios correspondientes de manera eficiente.

---

## 4. Tarea para la Casa Resuelta

1. **Mutation `UpdateTaskStatus`:**
   - Implementada en `core/schema.py`:
     - Argumentos: `id` (ID!) y `status` (String!).
     - Localiza la tarea mediante `tasks_visible_for(user)`.
     - Verifica que el usuario sea administrador del proyecto (`MembershipService.is_admin`).
     - Valida las reglas de transición de estado mediante `TaskSerializer(tarea, data={"status": status}, partial=True)`.
     - Emite el evento WebSocket `NotificationService.notify_task_updated(task)`.
2. **Comparativa: Cuándo usar REST vs. GraphQL en un proyecto real:**
   - **Caso para REST:** Endpoints de consumo público o de propósito simple (por ejemplo, una API para procesar pagos con webhooks o la descarga/subida de archivos binarios). REST ofrece soporte nativo de caché en CDN, códigos de estado universales y rate limiting simple por URL.
   - **Caso para GraphQL:** Una aplicación web o móvil con vistas dashboards complejas donde una pantalla necesita mostrar datos de usuarios, proyectos, estadísticas y tareas en simultáneo. GraphQL evita múltiples peticiones (evita *under-fetching*) y permite que la app móvil solicite solo los campos estrictamente visibles en pantalla reduciendo el consumo de datos celulares (evita *over-fetching*).
