from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ElencoViewSet,
    JogadorViewSet,
    FormacaoViewSet,
    FormacaoEscolhidaView,
    RegisterView,
    UserMeView,
)

router = DefaultRouter()
router.register(r'elencos', ElencoViewSet, basename='elenco')
router.register(r'jogadores', JogadorViewSet, basename='jogador')
router.register(r'formacoes', FormacaoViewSet, basename='formacao')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user_me'),
    
    # CORRIGIDO: Endpoint único para buscar (GET) e salvar (POST) a formação escolhida.
    path('formacao-escolhida/', FormacaoEscolhidaView.as_view(), name='formacao_escolhida'),
]