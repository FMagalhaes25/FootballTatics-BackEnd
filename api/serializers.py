from rest_framework import serializers
from .models import Elenco, Jogador, Formacao, FormacaoEscolhida, User
import json

class ElencoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elenco
        fields = '__all__'

class JogadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jogador
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    team_name = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'team_name']
        extra_kwargs = { 'password': {'write_only': True} }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Elenco.objects.create(
            tecnico=user, 
            nome_elenco=validated_data['team_name']
        )
        return user

class UserMeSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()
    elenco_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'team_name', 'elenco_id')

    def get_team_name(self, obj):
        elenco = obj.elencos.first()
        return elenco.nome_elenco if elenco else 'Time não definido'
    
    def get_elenco_id(self, obj):
        elenco = obj.elencos.first()
        return elenco.id if elenco else None

class FormacaoSerializer(serializers.ModelSerializer):
    posicoes = serializers.SerializerMethodField()
    class Meta:
        model = Formacao
        fields = '__all__'
    def get_posicoes(self, obj):
        try:
            return json.loads(obj.posicoes) if isinstance(obj.posicoes, str) else obj.posicoes
        except (json.JSONDecodeError, TypeError):
            return []

class FormacaoEscolhidaSerializer(serializers.ModelSerializer):
    formacao = FormacaoSerializer()
    class Meta:
        model = FormacaoEscolhida
        fields = ['formacao']
        
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserMeSerializer(self.user)
        data['user'] = serializer.data
        
        return data