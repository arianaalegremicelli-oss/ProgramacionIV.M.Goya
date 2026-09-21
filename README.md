# Ejercicios Resueltos - Clase 3
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Modelado Relacional (Project, Task, Tag), Serializers en DRF y Vistas `@api_view`

---

## 1. Modelado Relacional (`core/models.py`)

Se definieron las tres entidades del sistema y sus relaciones:
- **`Project`:** Modelo principal con `name`, `description` y `created_at`.
- **`Tag`:** Etiquetas con `name` único para categorización.
- **`Task`:** Tareas asociadas a un proyecto y con etiquetas:
  - `project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")`: Relación uno-a-muchos. Si se elimina el proyecto, se eliminan sus tareas en cascada.
  - `tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")`: Relación muchos-a-muchos.

---

## 2. Serializers en Django REST Framework (`core/serializers.py`)

Se implementaron serializadores basados en `serializers.ModelSerializer` para exponer los datos en formato JSON:
- `TagSerializer`: Serializa `id` y `name`.
- `TaskSerializer`: Serializa los campos de la tarea y anida las etiquetas mediante `TagSerializer(many=True, read_only=True)`.
- `ProjectSerializer`: Serializa los datos del proyecto y anida sus tareas mediante `TaskSerializer(many=True, read_only=True)`.

---

## 3. Endpoints Implementados (`core/views.py` y `core/urls.py`)

1. `GET /api/projects/`: Lista todos los proyectos con sus tareas anidadas.
2. `GET /api/tasks/`: Lista todas las tareas, aplicando optimización de consultas.
3. `GET /api/projects/<int:project_id>/` (**Tarea para la casa**):
   - Recupera el detalle de un proyecto específico según su ID.
   - Utiliza `get_object_or_404(Project, pk=project_id)` para retornar el objeto serializado con código `200 OK` si existe, o una respuesta `404 Not Found` automática si no se encuentra en la base de datos.

---

## 4. Tarea Teórica: `select_related` vs `prefetch_related`

Ambos métodos se utilizan en el ORM de Django para optimizar el rendimiento y resolver el problema de las **N+1 consultas**.

### `select_related`
- **Ámbito de uso:** Relaciones de tipo único: `ForeignKey` (muchos a uno) y `OneToOneField` (uno a uno).
- **Funcionamiento SQL:** Modifica la consulta SQL agregando un `JOIN` (`INNER JOIN` o `LEFT OUTER JOIN`). Recupera los datos de ambas tablas en una única consulta a la base de datos.

### `prefetch_related`
- **Ámbito de uso:** Relaciones con múltiples resultados: `ManyToManyField` (muchos a muchos) y `ForeignKey` inversa (uno a muchos).
- **Funcionamiento SQL:** Ejecuta consultas SQL independientes (generalmente dos) utilizando la cláusula `WHERE id IN (...)`, y posteriormente une y relaciona los objetos en la memoria de Python.
