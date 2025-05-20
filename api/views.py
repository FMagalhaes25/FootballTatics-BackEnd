from rest_framework import viewsets
from rest_framework import serializers
from .models import Elenco, Jogador
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ElencoSerializer, JogadorSerializer, UserRegisterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ElencoFilter, JogadorFilter
from rest_framework.permissions import IsAuthenticated


from rest_framework.permissions import IsAuthenticated


class ElencoViewSet(viewsets.ModelViewSet):
    serializer_class = ElencoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ElencoFilter

    def get_queryset(self):
        # Retorna apenas os elencos do técnico logado
        return Elenco.objects.filter(tecnico=self.request.user)

    def perform_create(self, serializer):
        # Salva o técnico como o usuário autenticado
        serializer.save(tecnico=self.request.user)
    
    
class JogadorViewSet(viewsets.ModelViewSet):
    serializer_class = JogadorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JogadorFilter

    def get_queryset(self):
        # Só retorna jogadores de elencos do técnico logado
        return Jogador.objects.filter(elenco__tecnico=self.request.user)

    def perform_create(self, serializer):
        elenco_id = self.request.data.get('elenco')
        if not Elenco.objects.filter(id=elenco_id, tecnico=self.request.user).exists():
            raise serializers.ValidationError("Você não tem permissão para adicionar jogador neste elenco.")
        
        serializer.save(elenco_id=elenco_id) 


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuário registrado com sucesso"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)