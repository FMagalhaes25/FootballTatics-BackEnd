from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O Email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

class Elenco(models.Model):
    tecnico = models.ForeignKey(User, related_name='elencos', on_delete=models.CASCADE)
    nome_elenco = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome_elenco

class Jogador(models.Model):
    elenco = models.ForeignKey(Elenco, related_name='jogadores', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    posicao = models.CharField(max_length=50)
    camisa = models.IntegerField()
    idade = models.IntegerField()
    
    nacionalidade = models.CharField(max_length=100, blank=True, null=True)
    
    velocidade = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    chute = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    passe = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    defesa = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    altura = models.IntegerField(default=180, help_text="Altura em cm")
    peso = models.IntegerField(default=75, help_text="Peso em kg")
    perna_boa = models.CharField(max_length=3, choices=[('DIR', 'Direita'), ('ESQ', 'Esquerda')], default='DIR')
    goleiro = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('elenco', 'camisa')

    def __str__(self):
        return self.nome

class Formacao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    estilo = models.CharField(max_length=100)
    dificuldade = models.IntegerField()
    descricao = models.TextField()
    categoria = models.CharField(max_length=100)
    posicoes = models.JSONField()

    def __str__(self):
        return self.nome

class FormacaoEscolhida(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    formacao = models.ForeignKey(Formacao, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.formacao.nome}"