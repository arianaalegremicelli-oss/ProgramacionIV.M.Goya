# Ejercicios Resueltos - Clase 4
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** CRUD Completo con ModelViewSet, DefaultRouter, Códigos HTTP, Manejo Global de Errores y Reglas de Negocio

---

## 1. ViewSets y Routers (`core/views.py` y `core/urls.py`)

- Se reemplazaron las vistas funcionales por clases `ModelViewSet`:
  - `ProjectViewSet(viewsets.ModelViewSet)`
  - `TaskViewSet(viewsets.ModelViewSet)`
  - `TagViewSet(viewsets.ModelViewSet)`
- Se configuró `DefaultRouter` en `core/urls.py`, lo que genera de forma automática el mapeo de rutas REST estándar para todas las operaciones CRUD (list, retrieve, create, update, partial_update, destroy).

---

## 2. Manejo Centralizado de Excepciones (`core/exceptions.py`)

- Se implementó la función `custom_exception_handler` y se configuró en `config/settings.py` bajo `REST_FRAMEWORK["EXCEPTION_HANDLER"]`.
- Intercepta los errores procesados por DRF y los encapsula en una estructura JSON uniforme:
  ```json
  {
    "error": true,
    "detail": ...
  }
  ```
- Para excepciones internas no controladas (código 500), devuelve una respuesta estandarizada `{"error": true, "detail": "Error interno del servidor."}` sin filtrar información interna del sistema.

---

## 3. Validaciones de Negocio en Serializers (`core/serializers.py`)

1. **Validación de campo individual (`validate_due_date`):**
   - Comprueba que la fecha límite no pertenezca al pasado (`due_date < date.today()`). De lo contrario, genera un `serializers.ValidationError`.
2. **Validación cruzada 1:**
   - No se permite marcar una tarea con `status="completada"` si no cuenta con fecha límite (`due_date`) registrada.
3. **Validación cruzada 2 (Tarea para la casa):**
   - Una tarea no puede asignarse con `status="en_progreso"` si su proyecto no posee al menos una tarea previa con `status="completada"`.
   - Se implementó en el método `validate(self, data)` mediante la consulta al ORM: `project.tasks.filter(status="completada").exists()`, excluyendo la instancia actual si se trata de una actualización.

---

## 4. Registro de Pruebas con `curl` (`pruebas_curl_codigos_http.txt`)

Se ejecutaron pruebas para verificar los 6 códigos de estado HTTP requeridos:
- **`200 OK`**: Petición `GET /api/projects/` exitosa.
- **`201 Created`**: Petición `POST /api/projects/` creando un recurso válido.
- **`204 No Content`**: Petición `DELETE /api/projects/<id>/` eliminando un recurso existente.
- **`400 Bad Request`**: Petición `POST /api/tasks/` violando reglas de validación (fecha pasada o estado inválido).
- **`404 Not Found`**: Petición `GET /api/projects/9999/` sobre un recurso inexistente.
- **`405 Method Not Allowed`**: Petición `DELETE /api/health/` sobre un endpoint que solo permite método GET.
