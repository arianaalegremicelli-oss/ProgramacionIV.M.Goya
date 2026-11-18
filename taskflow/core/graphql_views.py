# taskflow/core/graphql_views.py
# Alumna: Ariana Alegre Micelli

from graphene_django.views import GraphQLView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTGraphQLView(GraphQLView):
    """Integra autenticación JWT de DRF en la vista estándar de Graphene-Django."""

    def dispatch(self, request, *args, **kwargs):
        try:
            result = JWTAuthentication().authenticate(request)
        except AuthenticationFailed:
            result = None
        if result is not None:
            request.user, _ = result
        return super().dispatch(request, *args, **kwargs)
