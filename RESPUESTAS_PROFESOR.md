# Ejercicios Resueltos - Clase 12
**Materia:** Programación IV (TaskFlow)  
**Alumna:** Ariana Alegre Micelli  
**Tema:** Testing Automatizado (pytest), Integración Continua (GitHub Actions), Dockerización y Despliegue

---

## 1. Testing Automatizado y Fixtures

- **Configuración (`pytest.ini` y `conftest.py`):**
  - Fixture global `entorno_de_test` con `autouse=True`:
    - Desacoplamiento de Redis mediante `InMemoryChannelLayer`.
    - Aislamiento de llamadas externas sustituyendo `HolidayService.get_holidays` por un doble de prueba (*mock*) con `monkeypatch`.
    - Eliminación de rate limits (`DEFAULT_THROTTLE_CLASSES = []`) para prevenir falsos positivos (429) en pruebas de carga.
  - Fixtures `ana`, `beto`, `proyecto` y `cliente` (`APIClient`).
- **Batería de Pruebas Unitarias y de Integración:**
  - `core/tests/test_services.py`: evaluación de lógica de completado con/sin fecha límite y verificación del servicio de feriados.
  - `core/tests/test_views.py`: verificación de 401 en endpoints privados, control de acceso multitenant (aislamiento por proyecto) y permisos de creación (admin vs. miembro).

---

## 2. Integración Continua (CI) y Contenedorización

- **Pipeline de GitHub Actions (`.github/workflows/ci.yml`):**
  - Desencadenado en `push` y `pull_request` a la rama `main`.
  - Entorno `ubuntu-latest` con Python 3.12, instalación de dependencias y ejecución de tests con reporte de cobertura (`pytest --cov=core`).
- **Docker y Orquestación:**
  - `Dockerfile`: imagen ligera `python:3.12-slim`, separación del paso `COPY requirements.txt` para caché de capas, recolección de estáticos (`collectstatic`) y comando de arranque con Daphne.
  - `docker-compose.yml`: orquestación de servicios `web`, `db` (PostgreSQL 16 con comprobación de salud `pg_isready`) y `redis` (Redis 7) con persistencia en volumen `pgdata`.

---

## 3. Respuestas a Preguntas de Repaso

### 1. La Pirámide de Tests
```
       /      /  \       E2E (Puntas a punta): Pocos (Selenium / Playwright)
     / E2E\      Prueba el flujo completo en un navegador real.
    /------   /        \    Integración: Cantidad intermedia
  / Integr.  \   Prueba endpoints con cliente HTTP simulado, vistas y ORM juntos.
 /------------/  Unitarios   \ Unitarios: Base masiva de la pirámide
----------------  Funciones de servicio y validaciones aisladas en memoria.
```
*¿Por qué hay pocos tests E2E?* Porque son lentos de ejecutar, costosos de mantener e inestables ante cambios estéticos del frontend (*flaky tests*).

### 2. Patrón AAA y Principios FIRST
- **AAA (Arrange, Act, Assert):** Estructura clara en tres bloques: 1. Preparar el escenario y datos; 2. Ejecutar la acción bajo prueba; 3. Comprobar que el resultado obtenido coincide con el esperado.
- **FIRST:**
  - **F (Fast):** Ejecución rápida para correrse continuamente.
  - **I (Independent):** Ningún test depende del resultado de otro.
  - **R (Repeatable):** Mismo resultado en cualquier computadora o entorno de CI.
  - **S (Self-validating):** El test determina por sí mismo si pasó o falló (sin revisión manual).
  - **T (Timely):** Escritos en conjunto con el código productivo.

### 3. Dobles de Prueba: Stub vs. Mock vs. Fake
- **Stub:** Devuelve respuestas fijas predefinidas sin lógica (ej. una función falsa de feriados que siempre retorna una fecha).
- **Mock:** Registra y verifica cómo fue invocado (número de llamadas, parámetros enviados).
- **Fake:** Implementación funcional real simplificada no apta para producción (ej. base de datos SQLite en memoria en lugar de PostgreSQL).

### 4. Aislamiento de Base de Datos en `pytest-django`
Cada test que utiliza `@pytest.mark.django_db` corre dentro de una transacción atómica de base de datos. Al concluir el test, el framework ejecuta automáticamente un *rollback*, devolviendo la base de datos a su estado inicial e impidiendo efectos colaterales entre tests.

### 5. Cobertura de Líneas vs. Cobertura de Ramas
- **Líneas (Statement Coverage):** Mide el porcentaje de líneas de código que fueron ejecutadas al menos una vez.
- **Ramas (Branch Coverage):** Mide si se evaluaron todos los caminos posibles de cada bifurcación lógica (`if`/`else`). Una cobertura de líneas del 100% puede omitir evaluar el caso `else` implícito.

### 6. Prácticas de Trabajo en Integración Continua (CI)
Más allá de la herramienta, implica: 1. Integrar código a la rama principal con alta frecuencia (diariamente); 2. Mantener la rama principal siempre en verde; 3. Resolver inmediatamente cualquier rotura del pipeline como máxima prioridad del equipo.

### 7. Entrega Continua (Continuous Delivery) vs. Despliegue Continuo (Continuous Deployment)
- **Entrega Continua:** El código probado queda listo para producción automáticamente, pero la liberación final requiere aprobación humana manual (un clic).
- **Despliegue Continuo:** Cada cambio que supera el pipeline de pruebas se despliega a los servidores de producción de forma 100% automatizada sin intervención humana.

### 8. Conceptos en GitHub Actions
- **Workflow:** Proceso automatizado completo definido en un archivo `.yml`.
- **Job:** Conjunto de pasos que se ejecutan en una misma máquina virtual.
- **Step:** Tarea individual secuencial dentro de un job (ej. ejecutar un comando de consola).
- **Runner:** Servidor virtual o contenedor que hospeda y corre el job.
- **Action:** Bloque de código reutilizable de la comunidad (ej. `actions/checkout@v4`).

### 9. Contenedores vs. Máquinas Virtuales; Imagen, Contenedor y Registro
- **Contenedores vs. VMs:** Las VMs virtualizan el hardware completo y corren un SO invitado entero (pesadas); los contenedores comparten el kernel del host y aíslan únicamente el espacio de usuario (ligeros y de arranque instantáneo).
- **Imagen:** Plantilla inmutable de solo lectura con el código y las dependencias (el instalador).
- **Contenedor:** Instancia viva en ejecución de una imagen.
- **Registro:** Repositorio en la nube donde se almacenan y distribuyen imágenes (ej. Docker Hub).

### 10. Paridad Desarrollo/Producción y rol de `docker-compose`
Establece que los entornos de desarrollo, prueba y producción deben ser lo más idénticos posible. `docker-compose` garantiza esta paridad al permitir que en la máquina local se levanten exactamente los mismos motores de base de datos (PostgreSQL) y brokers (Redis) que corren en producción.

### 11. Los Tres Pilares de la Observabilidad
1. **Métricas:** Valores numéricos agregados a lo largo del tiempo (CPU, memoria, latencia de endpoints HTTP, tasa de errores 5xx).
2. **Logs:** Registros textuales fechados de eventos discretos ocurridos en la aplicación (`SecurityLog`).
3. **Trazas (Traces):** Seguimiento del ciclo de vida de una petición individual a través de múltiples microservicios o capas del sistema.

### 12. Versionado Semántico (SemVer: `MAJOR.MINOR.PATCH`)
- **PATCH (ej. 1.0.1):** Corrección de errores interna compatible hacia atrás (ej. solucionar el ordenamiento de una query).
- **MINOR (ej. 1.1.0):** Nueva funcionalidad compatible hacia atrás (ej. agregar el endpoint `GET /api/projects/<id>/summary/`).
- **MAJOR (ej. 2.0.0):** Cambio incompatible que rompe la API anterior (ej. renombrar un campo requerido en el JSON o alterar el esquema de autenticación).

### 13. Estrategias de Despliegue y Migraciones
- **Gradual (Rolling):** Se actualizan las instancias una por una detrás del balanceador.
- **Azul-Verde (Blue-Green):** Se levanta el nuevo ambiente (Verde) en paralelo al actual (Azul) y se conmuta el balanceador de golpe.
- **Canario (Canary):** Se deriva una pequeña fracción del tráfico real (ej. 5%) a la versión nueva para monitorear errores antes de extenderla a todos.
- *Problema de las migraciones en el Rollback:* Si la versión nueva alteró la base de datos (eliminó columnas o modificó tipos), volver a la versión vieja de la aplicación fallará si el código anterior no es compatible con el nuevo esquema relacional.

---

## 4. Tarea para la Casa Resuelta

- Entorno de testing completo con 7 tests automatizados passing en `core/tests/`.
- Pipeline de GitHub Actions configurado en `.github/workflows/ci.yml`.
- Entorno de producción con WhiteNoise (`settings.py`), contenedor `Dockerfile` y orquestador multi-contenedor `docker-compose.yml` vinculando Django, PostgreSQL y Redis.
