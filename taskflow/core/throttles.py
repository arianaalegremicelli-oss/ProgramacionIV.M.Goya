# taskflow/core/throttles.py
# Alumna: Ariana Alegre Micelli

from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Límite estricto de 5 intentos por minuto por IP para el endpoint de login."""

    scope = "login"

    def get_cache_key(self, request, view):
        ip = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ip}
