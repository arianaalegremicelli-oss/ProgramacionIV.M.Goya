import csv
import json
import logging
import os
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand
from core.models import Task

# Configuracion del logger para la tarea domiciliaria
# Guarda los errores y warnings en import.log y tambien los muestra en consola
logger = logging.getLogger("import_tasks")
logger.setLevel(logging.INFO)

# Evitamos duplicar handlers si se llama varias veces
if not logger.handlers:
    log_file = "import.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


class Command(BaseCommand):
    help = "Importa tareas desde multiples proveedores (JSON, CSV, XML)"

    def handle(self, *args, **options):
        self.stdout.write(">>> Iniciando proceso de importacion multi-proveedor...")
        logger.info("Inicio de ejecucion del comando import_tasks")

        total = 0
        total += self._import_json("data/tasks_provider_a.json", source="proveedor_a")
        total += self._import_csv("data/tasks_provider_b.csv", source="proveedor_b")
        total += self._import_xml("data/tasks_provider_c.xml", source="proveedor_c")
        # Cuarto proveedor agregado para la tarea
        total += self._import_json("data/tasks_provider_d.json", source="proveedor_d")

        mensaje_exito = f"Importacion finalizada: {total} tareas cargadas en total."
        logger.info(mensaje_exito)
        self.stdout.write(self.style.SUCCESS(mensaje_exito))

    def _import_json(self, path, source):
        count = 0
        if not os.path.exists(path):
            msg = f"No se encontro el archivo JSON en {path}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
            return 0

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                if self._crear_task(item, source):
                    count += 1
        except json.JSONDecodeError as e:
            msg = f"Error al decodificar JSON en {path}: {e}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
        return count

    def _import_csv(self, path, source):
        count = 0
        if not os.path.exists(path):
            msg = f"No se encontro el archivo CSV en {path}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
            return 0

        try:
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if self._crear_task(row, source):
                        count += 1
        except Exception as e:
            msg = f"Error leyendo CSV en {path}: {e}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
        return count

    def _import_xml(self, path, source):
        count = 0
        if not os.path.exists(path):
            msg = f"No se encontro el archivo XML en {path}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
            return 0

        try:
            tree = ET.parse(path)
            for task_el in tree.getroot().findall("task"):
                title_el = task_el.find("title")
                priority_el = task_el.find("priority")
                status_el = task_el.find("status")

                item = {
                    "title": title_el.text if title_el is not None else None,
                    "priority": priority_el.text if priority_el is not None else "media",
                    "status": status_el.text if status_el is not None else "pendiente",
                }
                if self._crear_task(item, source):
                    count += 1
        except ET.ParseError as e:
            msg = f"Error parseando XML en {path}: {e}"
            logger.error(msg)
            self.stderr.write(self.style.ERROR(msg))
        return count

    def _crear_task(self, item, source):
        # Validacion: si el titulo esta vacio o es None, lo ignoramos y avisamos con WARNING
        if not item.get("title"):
            warning_msg = f"[{source}] Registro sin titulo ignorado: {item}"
            logger.warning(warning_msg)
            self.stderr.write(self.style.WARNING(warning_msg))
            return False

        Task.objects.create(
            title=item["title"],
            priority=item.get("priority", "media"),
            status=item.get("status", "pendiente"),
            source=source,
        )
        return True
