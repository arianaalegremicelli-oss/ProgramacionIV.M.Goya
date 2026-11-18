# taskflow/core/permissions.py
# Alumna: Ariana Alegre Micelli

import logging
from rest_framework import permissions
from .models import SecurityLog
from .services import MembershipService

security_logger = logging.getLogger("security")


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, "project") else obj

        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)

        is_admin = MembershipService.is_admin(request.user, project)
        if not is_admin and MembershipService.is_member(request.user, project):
            ip = getattr(request, "META", {}).get("REMOTE_ADDR")
            SecurityLog.objects.create(
                action="permission_denied",
                user=request.user,
                detail=f"intento de escritura en proyecto {project.id}",
                ip_address=ip,
            )
            security_logger.warning(
                f"Permiso denegado a {request.user} en proyecto {project.id} desde {ip}"
            )
        return is_admin
