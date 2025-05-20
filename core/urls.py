from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

#Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API para criação e controle dos Elencos de Futebol",
        default_version='v1',
        description="Documentação da API para criação e controle dos Elencos de Futebol",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
