from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ElencoViewSet, JogadorViewSet, RegisterView, UserMeView
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Football Tatics API",
        default_version='v1',
        description="Documentação da API do projeto Football Tatics",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Rotas dos ViewSets
router = DefaultRouter()
router.register(r'elenco', ElencoViewSet, basename='elenco')
router.register(r'jogador', JogadorViewSet, basename='jogador')

urlpatterns = [
    # API REST
    path('', include(router.urls)),

    # Autenticação JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Cadastro de usuário 
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserMeView.as_view(), name='user-me'),

    # Swagger UI
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Recuperação de senha
    path('password/reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
