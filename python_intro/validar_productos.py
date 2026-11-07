# ==============================================================================
# Modulo de Validacion de Productos
# Alumna: Ariana Alegre Micelli
# Materia: Programacion IV
# ==============================================================================

import json


def validar_datos(nombre_archivo):
    """
    Valida un archivo JSON verificando formato de lista y precios numericos.
    Retorna la lista de datos si es valida, o None si ocurre un error.
    """
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as archivo_json:
            datos = json.load(archivo_json)

        if not isinstance(datos, list):
            raise ValueError("El archivo no contiene una lista de datos.")

        for item in datos:
            precio = item.get("precio")
            if not isinstance(precio, (int, float)):
                nombre = item.get("nombre", "Desconocido")
                raise TypeError(f"El precio del producto '{nombre}' no es numerico.")

        return datos

    except FileNotFoundError:
        print(f"Error: El archivo '{nombre_archivo}' no se encontro.")
        return None
    except json.JSONDecodeError:
        print("Error: El archivo no tiene un formato JSON valido.")
        return None
    except (ValueError, TypeError) as e:
        print(f"Error en la validacion de datos: {e}")
        return None
