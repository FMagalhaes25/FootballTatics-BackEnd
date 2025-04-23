from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Elenco(models.Model):
    nome = models.CharField(max_length=100)
    tecnico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elencos')
    
    def __str__(self):
        return self.nome

    
    
class Posicao(models.TextChoices):
    GOLEIRO = 'GOL', 'Goleiro'
    ZAGUEIRO = 'ZAG', 'Zagueiro'
    LATERAL_DIREITO = 'LD', 'Lateral Direito'
    LATERAL_ESQUERDO = 'LE', 'Lateral Esquerdo'
    VOLANTE = 'VOL', 'Volante'
    MEIA_CENTRAL = 'MC', 'Meia Central'
    MEIA_ATACANTE = 'MAT', 'Meia Atacante'
    PONTA_DIREITA = 'PD', 'Ponta Direita'
    PONTA_ESQUERDA = 'PE', 'Ponta Esquerda'
    CENTRO_AVANTE = 'CA', 'Centro Avante'
    
    
class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    altura = models.DecimalField(max_digits=4, decimal_places=2)
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    perna_boa = models.CharField(max_length=3, choices=[('DIR', 'Direita'), ('ESQ', 'Esquerda')])
    posicao = models.CharField(
        max_length=3,
        choices=Posicao.choices,
        default=Posicao.CENTRO_AVANTE,
    )
    camisa = models.IntegerField()
    velocidade = models.IntegerField()
    chute = models.IntegerField()
    passe = models.IntegerField()
    defesa = models.IntegerField()
    goleiro = models.BooleanField(default=False)
    elenco = models.ForeignKey(Elenco, on_delete=models.CASCADE, related_name='jogadores')

    def __str__(self):
        return f"{self.nome} - {self.get_posicao_display()}"
    
    
