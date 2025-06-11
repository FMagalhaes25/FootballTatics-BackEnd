from django.urls import path, include
from .views import MyTokenObtainPairView 
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ElencoViewSet, JogadorViewSet, RegisterView, UserMeView,
    FormacaoViewSet, SalvarFormacaoView, FormacaoEscolhidaView,
    SugerirTaticaView, ProcurarTalentosView

)

router = DefaultRouter()
router.register(r'elencos', ElencoViewSet, basename='elenco')
router.register(r'jogadores', JogadorViewSet, basename='jogador')
router.register(r'formacoes', FormacaoViewSet, basename='formacao')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='user_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user_me'),
    path('salvar-formacao/', SalvarFormacaoView.as_view(), name='salvar_formacao'),
    path('formacao-escolhida/', FormacaoEscolhidaView.as_view(), name='formacao_escolhida'),
    path('sugerir-tatica/', SugerirTaticaView.as_view(), name='sugerir_tatica'),
    path('procurar-talentos/', ProcurarTalentosView.as_view(), name='procurar_talentos'),
]
