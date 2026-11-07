# taskflow/core/permissions.py
# Alumna: Ariana Alegre Micelli

from rest_framework import permissions
from .services import MembershipService


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier miembro del proyecto puede leer (GET, HEAD, OPTIONS).
    Solo un admin del proyecto puede modificar (POST, PUT, PATCH, DELETE).
    Compatible con Task (obj.project) y con Project (obj).
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, "project") else obj
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)
        return MembershipService.is_admin(request.user, project)
