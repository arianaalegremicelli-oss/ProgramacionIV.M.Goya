from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router automatico que genera todas las rutas CRUD para los ViewSets
router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(r"tasks", views.TaskViewSet, basename="task")
router.register(r"tags", views.TagViewSet, basename="tag")

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("health/version/", views.health_version, name="health_version"),
    path("", include(router.urls)),
]
