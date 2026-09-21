# Ejercicios Resueltos - Clase 1
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Fundamentos de Python, Entorno de Desarrollo, Arquitectura Cliente-Servidor y Primeros Endpoints

---

## 1. Fundamentos de Python (Manejo de Archivos y Modularización)

Estructura en la carpeta `python_intro/`:
- `datos.csv`: Archivo con datos tabulares de productos, precios y stock.
- `validar_productos.py`: Módulo que contiene la función `validar_datos(nombre_archivo)` para verificar que el archivo JSON exista, contenga una lista y que los precios sean de tipo numérico (`int` o `float`), usando bloques `try/except` para capturar errores de tipo o formato.
- `app.py`: Script principal que lee `datos.csv` usando `csv.DictReader`, castea los valores a enteros, calcula el promedio de precios con la función `calcular_promedio_precio`, exporta los datos a `salida.json` y los valida llamando a `validar_datos`.

---

## 2. Configuración del Proyecto TaskFlow (Django)

- Proyecto inicializado con `django-admin startproject config .` y app creada con `python manage.py startapp core`.
- Se configuraron las dependencias en `requirements.txt` y se registraron `rest_framework` y `core` dentro de `INSTALLED_APPS` en `config/settings.py`.
- Configuración de entorno con `python-dotenv`: los valores de `SECRET_KEY` y `DEBUG` se leen desde el archivo `.env`.
- Archivo `.gitignore` configurado para ignorar `venv/`, `.env`, `db.sqlite3` y archivos de caché `__pycache__/`.

### Endpoints implementados (`core/views.py` y `core/urls.py`):
1. **Endpoint base:** `GET /api/health/`
   - Devuelve: `{"status": "ok", "service": "TaskFlow API"}`
2. **Endpoint de versión (Tarea para la casa):** `GET /api/health/version/`
   - Devuelve: `{"version": "0.1.0"}`

---

## 3. Tarea Teórica: Diferencia entre GET y POST

### ¿Cuál es la diferencia entre los métodos HTTP GET y POST?
- **GET:** Se utiliza para solicitar y leer información del servidor sin modificar el estado del sistema. Los parámetros se envían visibles a través de la URL (Query String) y la petición es segura e idempotente (hacerla varias veces produce el mismo resultado).
- **POST:** Se utiliza para enviar datos al servidor con el fin de crear un nuevo recurso o realizar una acción que modifica el estado. Los datos se envían dentro del cuerpo de la petición (HTTP Body) y no es una operación idempotente.

### ¿Por qué GET no debería usarse para modificar datos?
1. **Idempotencia y seguridad:** Por estándar HTTP, los clientes (como los navegadores) asumen que las peticiones GET son de solo lectura.
2. **Caché y precarga:** Los navegadores y proxies intermedios guardan en caché o precargan enlaces GET en segundo plano. Si un GET modificara o eliminara datos, se podrían ejecutar cambios no deseados automáticamente.
3. **Indexación de motores de búsqueda:** Los bots y rastreadores web siguen los enlaces GET. Si un GET realizara modificaciones, un crawler podría alterar o borrar registros de la base de datos al recorrer el sitio.
4. **Visibilidad en historial y logs:** Los parámetros enviados por GET quedan registrados en el historial de navegación, en los marcadores y en los logs de acceso del servidor, exponiendo información sensible.
