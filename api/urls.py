from rest_framework.routers import DefaultRouter
from .views import ElencoViewSet, JogadorViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'elenco', ElencoViewSet, basename='elenco')
router.register(r'jogador', JogadorViewSet, basename='jogador')

urlpatterns = [
    path('', include(router.urls)),
]
