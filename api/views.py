from rest_framework import viewsets
from rest_framework import serializers
from .models import Elenco, Jogador, Formacao, FormacaoEscolhida
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ElencoSerializer, JogadorSerializer, UserRegisterSerializer, UserMeSerializer, FormacaoSerializer, FormacaoEscolhidaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ElencoFilter, JogadorFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet


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
        try:
            elenco = Elenco.objects.get(tecnico=self.request.user)
        except Elenco.DoesNotExist:
            raise serializers.ValidationError("Usuário não possui elenco cadastrado.")
        
        serializer.save(elenco=elenco)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuário registrado com sucesso"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)
    
    
class FormacaoViewSet(ReadOnlyModelViewSet):  
    queryset = Formacao.objects.all()
    serializer_class = FormacaoSerializer
    permission_classes = []
    
    
class SalvarFormacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        formacao_id = request.data.get('formationId')
        if not formacao_id:
            return Response({'error': 'formationId é obrigatório'}, status=400)

        try:
            formacao = Formacao.objects.get(id=formacao_id)
        except Formacao.DoesNotExist:
            return Response({'error': 'Formação não encontrada'}, status=404)

        FormacaoEscolhida.objects.update_or_create(
            user=request.user,
            defaults={'formacao': formacao}
        )

        return Response({'message': 'Formação salva com sucesso'}, status=200)
    

class FormacaoEscolhidaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            formacao_escolhida = FormacaoEscolhida.objects.select_related("formacao").get(user=request.user)
            serializer = FormacaoEscolhidaSerializer(formacao_escolhida)
            return Response(serializer.data, status=200)
        except FormacaoEscolhida.DoesNotExist:
            return Response({'error': 'Nenhuma formação escolhida'}, status=404)