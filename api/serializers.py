from rest_framework import serializers
from .models import Elenco, Jogador


class ElencoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elenco
        fields = '__all__'
        
        
class JogadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jogador
        fields = '__all__'

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