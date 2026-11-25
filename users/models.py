from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        BIBLIOTHECAIRE = 'BIBLIOTHECAIRE', 'Bibliothécaire'
        ABONNE = 'ABONNE', 'Abonné'

    email = models.EmailField(unique=True)

    telephone = models.CharField(
        max_length=20,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ABONNE
    )

    def __str__(self):
        return self.username