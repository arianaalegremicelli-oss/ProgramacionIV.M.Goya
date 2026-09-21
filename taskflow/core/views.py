from django.http import JsonResponse

# Vista basica de health check pedida en la clase
def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})

# Tarea domiciliaria: Endpoint que devuelve la version de la API
def health_version(request):
    return JsonResponse({"version": "0.1.0"})
