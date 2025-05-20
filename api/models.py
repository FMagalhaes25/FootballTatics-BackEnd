from django.db import models
from django.conf import settings
from uuid import uuid4
from django.contrib.auth.models import (AbstractUser, PermissionsMixin, BaseUserManager)

# Create your models here.
class Elenco(models.Model):
    nome = models.CharField(max_length=100)
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='elencos')
    
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
    
    
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    
    
class User(AbstractUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, verbose_name="ID do usuário"
    )
    name = models.CharField(max_length=150, verbose_name="Nome do usuário")
    email = models.EmailField(unique=True, verbose_name="Email do usuário")
    password = models.CharField(max_length=128, verbose_name="Senha do usuário")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefone do usuário")
    

    is_active = models.BooleanField(default=True, verbose_name="Usuário ativo")
    is_staff = models.BooleanField(default=False, verbose_name="Usuário staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Usuário superuser")

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]
    objects = UserManager()


    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["email"]

    def __str__(self):
        return self.email
