# --- Imports do Django e DRF ---
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView

# --- Imports de outros módulos do projeto ---
from .models import Elenco, Jogador, Formacao, FormacaoEscolhida
from .filters import ElencoFilter, JogadorFilter

# --- IMPORTAÇÃO CORRIGIDA DE SERIALIZERS ---
from .serializers import (
    ElencoSerializer, JogadorSerializer, UserRegisterSerializer,
    UserMeSerializer, FormacaoSerializer, FormacaoEscolhidaSerializer,
    MyTokenObtainPairSerializer
)

# --- IMPORTS PARA A LÓGICA DE IA ---
from django.conf import settings
from pathlib import Path
from tensorflow.keras.models import load_model
import joblib
from .ia_logic import recomendar_formacao_com_ia 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# VIEWS DE AUTENTICAÇÃO E USUÁRIO
# ==============================================================================

class MyTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = MyTokenObtainPairSerializer

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

# ==============================================================================
# VIEWSETS PARA O CRUD (JOGADOR, ELENCO, FORMAÇÃO)
# ==============================================================================

class ElencoViewSet(viewsets.ModelViewSet):
    serializer_class = ElencoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ElencoFilter

    def get_queryset(self):
        return Elenco.objects.filter(tecnico=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tecnico=self.request.user)

class JogadorViewSet(viewsets.ModelViewSet):
    serializer_class = JogadorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JogadorFilter

    def get_queryset(self):
        # Garante que o técnico só veja jogadores dos seus próprios elencos
        return Jogador.objects.filter(elenco__tecnico=self.request.user)

class FormacaoViewSet(ReadOnlyModelViewSet):
    queryset = Formacao.objects.all()
    serializer_class = FormacaoSerializer
    permission_classes = []

# ==============================================================================
# VIEWS DE LÓGICA DE NEGÓCIO (SALVAR FORMAÇÃO, SUGESTÕES, ETC.)
# ==============================================================================

class SalvarFormacaoView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        formacao_id = request.data.get('formationId')
        if not formacao_id:
            return Response({'error': 'formationId é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            formacao = Formacao.objects.get(id=formacao_id)
        except Formacao.DoesNotExist:
            return Response({'error': 'Formação não encontrada'}, status=status.HTTP_404_NOT_FOUND)
        FormacaoEscolhida.objects.update_or_create(user=request.user, defaults={'formacao': formacao})
        return Response({'message': 'Formação salva com sucesso'}, status=status.HTTP_200_OK)

class FormacaoEscolhidaView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            formacao_escolhida = FormacaoEscolhida.objects.select_related("formacao").get(user=request.user)
            serializer = FormacaoEscolhidaSerializer(formacao_escolhida)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FormacaoEscolhida.DoesNotExist:
            return Response({'error': 'Nenhuma formação escolhida'}, status=status.HTTP_404_NOT_FOUND)

class SugerirTaticaView(APIView):
    """ View que usa a lógica de IA para sugerir táticas baseadas no elenco do usuário. """
    permission_classes = [IsAuthenticated]

    try:
        BASE_DIR = settings.BASE_DIR
        model_path = BASE_DIR / 'ia_models' / 'modelspi2025_v12.h5'
        scaler_path = BASE_DIR / 'ia_models' / 'scaler_wh.pkl'

        modelo_ia_global = load_model(model_path)
        scaler_ia_global = joblib.load(scaler_path)
        logging.info("✅ Modelo de IA 'Procurando Talentos' e Scaler carregados com sucesso para SugerirTaticaView.")
    except Exception as e:
        modelo_ia_global = None
        scaler_ia_global = None
        logging.error(f"❌ ERRO ao carregar modelo de IA e Scaler para SugerirTaticaView: {e}")

    def get(self, request):
        if not SugerirTaticaView.modelo_ia_global or not SugerirTaticaView.scaler_ia_global:
            logging.error("Serviço de IA indisponível para SugerirTaticaView.")
            return Response(
                {"error": "Serviço de IA indisponível. Verifique os logs do servidor."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            jogadores_qs = Jogador.objects.filter(elenco__tecnico=request.user)
            lista_jogadores_serializada = list(jogadores_qs.values(
                'nome', 'posicao', 'altura', 'peso', 'velocidade', 'chute', 'passe', 'defesa', 'goleiro'
            ))
            
            logging.info(f"SugerirTaticaView: Jogadores do elenco encontrados: {len(lista_jogadores_serializada)}")
            
            resultado_sugestao = recomendar_formacao_com_ia(
                lista_jogadores_serializada,
                SugerirTaticaView.modelo_ia_global,
                SugerirTaticaView.scaler_ia_global
            )
            
            return Response({
                'sugestoes': resultado_sugestao.get('sugestoes', {}),
                'no_match': resultado_sugestao.get('no_match', True),
                'message': resultado_sugestao.get('message', 'Erro ao processar sugestões.')
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception("Ocorreu um erro interno na SugerirTaticaView:")
            return Response(
                {"error": f"Ocorreu um erro interno ao sugerir tática. Detalhe: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ==============================================================================
# VIEW DE ANÁLISE DE TALENTOS (USA LÓGICA DE IA PARA CLASSIFICAR JOGADORES)
# ==============================================================================

class ProcurarTalentosView(APIView):
    permission_classes = [IsAuthenticated]

    try:
        BASE_DIR = settings.BASE_DIR
        model_path = BASE_DIR / 'ia_models' / 'modelspi2025_v12.h5'
        scaler_path = BASE_DIR / 'ia_models' / 'scaler_wh.pkl'
        
        modelo_ia_talentos = load_model(model_path)
        scaler_ia_talentos = joblib.load(scaler_path)
        logging.info("✅ Modelo de IA 'Procurar Talentos' carregado com sucesso para ProcurarTalentosView.")

    except Exception as e:
        modelo_ia_talentos = None
        scaler_ia_talentos = None
        logging.error(f"❌ ERRO ao carregar modelo de IA para ProcurarTalentosView: {e}")


    def get(self, request):
        if not self.modelo_ia_talentos or not self.scaler_ia_talentos:
            logging.error("Serviço de IA de talentos indisponível.")
            return Response(
                {"error": "Serviço de IA de talentos indisponível. Verifique os logs do servidor."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            jogadores_qs = Jogador.objects.filter(elenco__tecnico=request.user)
            if not jogadores_qs.exists():
                return Response({"error": "Seu elenco não possui jogadores para a análise."}, status=status.HTTP_400_BAD_REQUEST)

            lista_jogadores_serializada = list(jogadores_qs.values(
                'nome', 'posicao', 'altura', 'peso', 'velocidade', 'chute', 'passe', 'defesa', 'goleiro'
            ))
            
            logging.info(f"ProcurarTalentosView: Jogadores do elenco encontrados: {len(lista_jogadores_serializada)}")

            resultado_ia = recomendar_formacao_com_ia(
                lista_jogadores_serializada,
                self.modelo_ia_talentos,
                self.scaler_ia_talentos
            )

            relatorio_talentos = []
            
            if 'jogadores_classificados' in resultado_ia:
                mapa_posicoes_sugeridas = {
                    j['nome']: j['posicao_sugerida'] 
                    for j in resultado_ia['jogadores_classificados']
                }
                
                for jogador_original in lista_jogadores_serializada:
                    posicao_sugerida = mapa_posicoes_sugeridas.get(
                        jogador_original['nome'], 
                        'Goleiro' if jogador_original.get('goleiro', False) else 'Sem Sugestão (AI)'
                    )
                    
                    relatorio_talentos.append({
                        "nome": jogador_original['nome'],
                        "posicao_atual": jogador_original['posicao'],
                        "posicao_sugerida": posicao_sugerida
                    })
            else:
                logging.error("ProcurarTalentosView: 'jogadores_classificados' não encontrado no resultado da IA. Retornando análise básica.")
                for jogador_original in lista_jogadores_serializada:
                    relatorio_talentos.append({
                        "nome": jogador_original['nome'],
                        "posicao_atual": jogador_original['posicao'],
                        "posicao_sugerida": "Goleiro" if jogador_original.get('goleiro', False) else "Análise Indisponível (Erro)"
                    })

            return Response(relatorio_talentos, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception("Ocorreu um erro interno na ProcurarTalentosView:")
            return Response(
                {"error": f"Ocorreu um erro interno na análise de talentos. Detalhe: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )