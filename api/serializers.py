from rest_framework import serializers
from .models import Elenco, Jogador, User, Formacao, FormacaoEscolhida
import json


class ElencoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elenco
        fields = '__all__'
        
        
class JogadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jogador
        fields = '__all__'
        extra_kwargs = {
            'elenco': {'required': False},  
        }

    #Validação para que o número da camisa seja único dentro do elenco e que os atributos do jogador sejam entre 0-10
    def validate(self, data):
        elenco = data.get('elenco') or self.initial_data.get('elenco')
        camisa = data.get('camisa')

        jogador_id = self.instance.id if self.instance else None

        if elenco and camisa:
            if Jogador.objects.filter(elenco_id=elenco, camisa=camisa).exclude(id=jogador_id).exists():
                raise serializers.ValidationError({
                    'camisa': 'Já existe um jogador com esse número nesse elenco.'
                })

        # Validação para que os atributos do jogador sejam entre 0-10
        for campo in ['velocidade', 'chute', 'passe', 'defesa']:
            valor = data.get(campo)
            if valor is not None and not 0 <= valor <= 10:
                raise serializers.ValidationError({
                    campo: f"O valor de '{campo}' deve estar entre 0 e 10."
                })

        return data
    
    
class UserRegisterSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'password', 'confirm_password', 'team_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password') 
        team_name = validated_data.pop('team_name')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data.get('name', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password']
        )

        Elenco.objects.create(nome=team_name, tecnico=user)
        return user
    
    
class UserMeSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    elenco = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone', 'elenco', 'team']

    def get_team(self, obj):
        elenco = Elenco.objects.filter(tecnico=obj).first()
        return elenco.nome if elenco else None
    
    def get_elenco(self, obj):
        elenco = Elenco.objects.filter(tecnico=obj).first()
        return elenco.id if elenco else None
    
    
class FormacaoSerializer(serializers.ModelSerializer):
    posicoes = serializers.SerializerMethodField()

    class Meta:
        model = Formacao
        fields = '__all__'

    def get_posicoes(self, obj):
        try:
            return json.loads(obj.posicoes)
        except json.JSONDecodeError:
            return []
        
        
class FormacaoEscolhidaSerializer(serializers.ModelSerializer):
    formacao = FormacaoSerializer()

    class Meta:
        model = FormacaoEscolhida
        fields = ['formacao']