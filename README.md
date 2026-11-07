# Ejercicios Resueltos - Clase 5
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Capa de Servicios, Repositorios, Paginación, Filtrado y Consumo de APIs Externas con Caché

---

## 1. Separación en Capas: Repositorio y Servicio

- **Repositorio (`core/repositories.py`):**
  - Implementación de `TaskRepository` con métodos centralizados:
    - `get_queryset()`: optimizado con `select_related("project")` y `prefetch_related("tags")`, ordenado de manera determinística por `-created_at`.
    - `get_by_project(project_id)`: filtro directo por proyecto reutilizando la optimización del queryset base.
- **Servicio (`core/services.py`):**
  - `TaskService.mark_completed(task)`: ejecuta la regla de negocio que exige fecha límite (`due_date`) antes de pasar el estado a `completada` y actualiza selectivamente con `save(update_fields=["status"])`.
  - `TaskService.tasks_overdue(queryset)`: filtra tareas vencidas no completadas comparando `due_date__lt=timezone.now().date()`.
  - `ProjectService.project_summary(project)`: calcula el resumen de tareas por estado utilizando agregación SQL (`values("status").annotate(total=Count("id"))`).
  - `HolidayService`: cliente para consultar feriados nacionales argentinos vía API externa `date.nager.at`, aplicando el patrón Cache-Aside con TTL de 24 horas y degradación elegante ante errores (fallback a lista vacía y reintento en 5 minutos).

---

## 2. Endpoints Personalizados y Filtros (`core/views.py` y `core/serializers.py`)

- **Acciones `@action` en ViewSets:**
  - `POST /api/tasks/<id>/complete/`: acción de detalle que delega en `TaskService.mark_completed`.
  - `GET /api/tasks/overdue/`: acción de lista paginada para tareas vencidas.
  - `GET /api/projects/<id>/summary/`: acción de detalle que devuelve el recuento de tareas por estado.
- **Filtros, Búsqueda y Ordenamiento:**
  - Habilitados en `TaskViewSet`: `filterset_fields = ["status", "priority", "project"]`, `search_fields = ["title", "description"]` y `ordering_fields = ["due_date", "created_at", "priority"]`.
- **Integración con Serializer:**
  - `due_on_holiday`: implementado como `SerializerMethodField` que invoca `HolidayService.is_holiday(obj.due_date)` sin impactar la base de datos local.

---

## 3. Respuestas a Preguntas de Repaso

### 1. Recorrido de una petición `POST /api/tasks/7/complete/`
1. **Red / URLs:** La petición llega a `core/urls.py` a través del `DefaultRouter`.
2. **Capa de Presentación (ViewSet):** `TaskViewSet.complete` recupera la instancia llamando a `self.get_object()`.
3. **Capa de Negocio (Servicio):** Se invoca `TaskService.mark_completed(task)`, donde se evalúa la regla de validación (`task.due_date`).
4. **Capa de Datos (ORM):** Se persiste el cambio en la base de datos mediante `task.save(update_fields=["status"])`.
5. **Serialización y Respuesta:** Se serializa el objeto actualizado mediante `TaskSerializer` y se responde con código HTTP 200 y el JSON resultante.

### 2. ¿Qué es una "vista gorda" y qué problemas trae?
Una "vista gorda" (*fat view*) ocurre cuando la capa controladora acumula validaciones de negocio, queries complejas y consumo de APIs externas. Dificulta las pruebas unitarias (obliga a simular peticiones HTTP completas), impide reutilizar la lógica en otros clientes (como tareas asincrónicas o GraphQL) y rompe el principio de responsabilidad única.

### 3. ¿Por qué validar tanto en el Serializer como en el Servicio?
Porque representan niveles distintos de defensa (*defensa en profundidad*). El serializer valida peticiones HTTP de creación/edición de datos de entrada (`PUT`/`PATCH`/`POST`), pero un cambio de estado invocado desde una acción específica (`/complete/`) o desde un comando interno del sistema no pasa necesariamente por el serializer. La regla debe residir en el servicio para garantizar consistencia siempre.

### 4. Diferencia entre un Repositorio y el ORM
El ORM es una herramienta genérica de mapeo objeto-relacional que construye SQL. El repositorio es un patrón arquitectónico de la aplicación que encapsula consultas específicas con nombres de dominio (`get_by_project`, `get_queryset`), estandariza optimizaciones (`select_related`) y aísla al resto del sistema de los detalles del motor de base de datos.

### 5. ¿Por qué `/overdue/` es GET y `/complete/` es POST?
`GET` debe ser seguro e idempotente: consultar tareas vencidas no altera el estado del servidor. `POST` se usa para operaciones no seguras que modifican el estado de un recurso (marcar una tarea como completada cambia campos en la base de datos).

### 6. Paginación por número de página vs. por cursor
- **Número de página:** Permite saltar a páginas específicas (`?page=3`) y calcular el total de páginas, pero es costoso en datasets gigantes (requiere `COUNT(*)`) e inestable si se insertan o eliminan filas mientras se navega.
- **Cursor:** Utiliza un puntero opaco e inmutable indexado (por ejemplo, timestamp o ID). Es altamente eficiente, ideal para scroll infinito o datos en tiempo real, pero no permite saltar a páginas arbitrarias.

### 7. Importancia de un ordenamiento estable al paginar
Si no se define un `order_by` determinístico, el motor de base de datos no garantiza el orden de retorno entre consultas consecutivas. Al paginar, una misma fila podría repetirse en dos páginas distintas o no aparecer en ninguna.

### 8. ¿Por qué declarar explícitamente los campos filtrables?
Por seguridad y rendimiento: previene la exposición accidental de campos internos o sensibles mediante consultas automáticas, y asegura que solo se filtren campos que posean índices en la base de datos.

### 9. Patrones de resiliencia en `HolidayService`
1. **Timeout estricto:** `requests.get(..., timeout=5)` evita que peticiones lentas o caídas de la API externa dejen colgados los workers del servidor.
2. **Caché (Cache-Aside):** Reduce a cero las llamadas innecesarias al servicio externo durante 24 horas.
3. **Degradación elegante (Graceful Degradation):** Si la API de feriados falla o responde con error, se captura la excepción, se asigna `[]` y la API propia sigue funcionando devolviendo `due_on_holiday: false`.

### 10. TTL de la caché y manejo de fallos
El TTL (*Time To Live*) define la caducidad del dato en memoria. Como el calendario de feriados es estático durante el año, un TTL de 24 horas es adecuado. En caso de fallo de red, se guarda una lista vacía con TTL de solo 5 minutos para evitar bloquear el servicio y a la vez reintentar pronto una vez restablecida la API externa.

### 11. ¿Cuándo persistir un dato y cuándo calcularlo al responder?
Se persiste cuando el dato es propio del negocio, debe ser consultado/filtrado masivamente o requiere auditoría histórica. Se calcula en tiempo de respuesta (usando caché si es costoso) cuando deriva de fuentes externas volátiles, depende del momento de la consulta o es fácilmente deducible sin afectar el rendimiento.

---

## 4. Tarea para la Casa Resuelta

1. **`ProjectService.project_summary(project)`**:
   - Implementado en `core/services.py` y expuesto en `GET /api/projects/<id>/summary/` dentro de `ProjectViewSet`.
   - Utiliza una única consulta SQL optimizada con `annotate(total=Count("id"))`.
2. **Investigación de Caché en Producción:**
   - Django utiliza `LocMemCache` por defecto (caché en memoria del proceso).
   - En entornos de producción con servidores multi-proceso o multi-instancia (Gunicorn/UWSGI/Daphne), cada proceso tiene su propio espacio de memoria aislado, lo que provocaría inconsistencias y múltiples llamadas externas redundantes. Se reemplaza por un almacén en memoria centralizado como **Redis**, permitiendo compartir la caché de forma atómica y persistente entre todos los procesos.
