import django_filters
from .models import Elenco, Jogador


class ElencoFilter(django_filters.FilterSet):
    class Meta:
        model = Elenco
        fields = '__all__'
        

class JogadorFilter(django_filters.FilterSet):
    class Meta:
        model = Jogador
        fields = '__all__'