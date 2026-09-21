# Ejercicios Resueltos - Clase 2
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** E/S de Datos (JSON, CSV, XML), Modelo Task, Migraciones y Management Command

---

## 1. Archivos de Proveedores de Datos (`data/`)

Se crearon las fuentes de datos de prueba para simular la recepción de información desde múltiples orígenes:
- `tasks_provider_a.json`: Formato JSON estructurado como lista de diccionarios.
- `tasks_provider_b.csv`: Formato CSV delimitado por comas con encabezados `title,priority,status`.
- `tasks_provider_c.xml`: Formato XML con estructura jerárquica `<tasks><task>...`.
- `tasks_provider_d.json` (Tarea para la casa): Archivo JSON que incluye un registro sin el campo obligatorio `title` para verificar la validación de datos.

---

## 2. Modelo `Task` y Migraciones (`core/models.py`)

Se definió el modelo `Task` con los siguientes campos:
- `title`: `models.CharField(max_length=200)`
- `priority`: `models.CharField` con opciones `baja`, `media`, `alta` (default: `media`).
- `status`: `models.CharField` con opciones `pendiente`, `en_progreso`, `completada` (default: `pendiente`).
- `source`: `models.CharField(max_length=50, blank=True)` para identificar el proveedor de origen.
- `created_at`: `models.DateTimeField(auto_now_add=True)`.

El modelo fue registrado en `core/admin.py` y se generaron y aplicaron las migraciones correspondientes (`0001_initial.py`).

---

## 3. Comando Personalizado: `import_tasks` (`core/management/commands/import_tasks.py`)

Se implementó el comando de gestión de Django para unificar la importación desde los distintos proveedores:
- **Ejecución:** `python manage.py import_tasks`
- **Manejo de formatos:** Métodos internos `_import_json`, `_import_csv` y `_import_xml` utilizando las librerías estándar `json`, `csv` y `xml.etree.ElementTree`.
- **Manejo de errores por proveedor:** Cada proveedor está encapsulado en bloques `try/except` para que si uno falla (archivo inexistente o corrupto), no detenga la importación de los demás.

### Tarea para la casa implementada:
1. **Validación de título:** En el método `_crear_task`, si un registro no posee el campo `title`, se descarta y se emite un `WARNING` sin interrumpir la ejecución.
2. **Módulo estándar `logging`:** Se reemplazó el uso directo de `stderr.write` por la configuración de un logger que escribe los eventos (`INFO`, `WARNING`, `ERROR`) en el archivo `import.log`.
3. **`.gitignore`:** Se agregó `import.log` para evitar versionar archivos de registro.
