# ==============================================================================
# Ejercicio Integrador - Clase 1
# Alumna: Ariana Alegre Micelli
# Materia: Programacion IV
# ==============================================================================

import csv
import json
from validar_productos import validar_datos


def calcular_promedio_precio(lista):
    """
    Calcula el precio promedio de una lista de productos.
    """
    if not lista:
        return 0
    total_precio = sum(p['precio'] for p in lista)
    return total_precio / len(lista)


# Lectura de datos.csv y casteo de tipos
productos_desde_csv = []
try:
    with open("datos.csv", mode="r", encoding="utf-8") as archivo_csv:
        lector_diccionario = csv.DictReader(archivo_csv)
        for fila in lector_diccionario:
            fila["id"] = int(fila["id"])
            fila["precio"] = int(fila["precio"])
            fila["stock"] = int(fila["stock"])
            productos_desde_csv.append(fila)
except FileNotFoundError:
    print("Error: El archivo 'datos.csv' no se encontro.")

# Calculo de promedio
if productos_desde_csv:
    promedio = calcular_promedio_precio(productos_desde_csv)
    print(f"El precio promedio de los productos es: ${promedio:.2f}")

# Exportacion a JSON y validacion con modulo externo
if productos_desde_csv:
    datos_json = json.dumps(productos_desde_csv, indent=4)
    with open("salida.json", "w", encoding="utf-8") as archivo_salida:
        archivo_salida.write(datos_json)

    datos_validados = validar_datos("salida.json")
    if datos_validados is not None:
        print(f"Validacion completada exitosamente. Total items: {len(datos_validados)}")
