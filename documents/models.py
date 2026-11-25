from django.conf import settings
from django.utils import timezone
from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class Document(models.Model):

    class TypeDocument(models.TextChoices):
        LIVRE = 'LIVRE', 'Livre'
        THESE = 'THESE', 'Thèse'
        MEMOIRE = 'MEMOIRE', 'Mémoire'
        ARTICLE = 'ARTICLE', 'Article'

    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=150)

    isbn = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    annee_publication = models.PositiveSmallIntegerField()

    type_document = models.CharField(
        max_length=20,
        choices=TypeDocument.choices
    )

    description = models.TextField(blank=True)

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name='documents'
    )

    def __str__(self):
        return self.titre


class Exemplaire(models.Model):

    class Etat(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        EMPRUNTE = 'EMPRUNTE', 'Emprunté'
        INDISPONIBLE = 'INDISPONIBLE', 'Indisponible'

    code_inventaire = models.CharField(
        max_length=50,
        unique=True
    )

    etat = models.CharField(
        max_length=20,
        choices=Etat.choices,
        default=Etat.DISPONIBLE
    )

    emplacement = models.CharField(
        max_length=100,
        blank=True
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.PROTECT,
        related_name='exemplaires'
    )

    def __str__(self):
        return self.code_inventaire


class Emprunt(models.Model):

    class Statut(models.TextChoices):
        DEMANDEE = 'DEMANDEE', 'Demandée'
        EN_COURS = 'EN_COURS', 'En cours'
        REFUSEE = 'REFUSEE', 'Refusée'
        TERMINEE = 'TERMINEE', 'Terminée'

    date_demande = models.DateTimeField(default=timezone.now)

    date_emprunt = models.DateTimeField(
        null=True,
        blank=True
    )

    date_limite = models.DateField(
        null=True,
        blank=True
    )

    date_retour = models.DateField(
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.DEMANDEE
    )

    duree_appliquee = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    abonne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='emprunts'
    )

    exemplaire = models.ForeignKey(
        Exemplaire,
        on_delete=models.PROTECT,
        related_name='emprunts'
    )

    bibliothecaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='emprunts_traites',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.abonne} - {self.exemplaire}"
class Penalite(models.Model):
    emprunt = models.OneToOneField(
        Emprunt,
        on_delete=models.CASCADE,
        related_name="penalite"
    )

    jours_retard = models.PositiveIntegerField(default=0)

    montant = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pénalité de l'emprunt #{self.emprunt_id}"



class ParametresBibliotheque(models.Model):
    duree_emprunt = models.PositiveSmallIntegerField(
        default=14,
        verbose_name="Durée d'emprunt (jours)"
    )

    tarif_penalite = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=2.00,
        verbose_name="Pénalité par jour (DH)"
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Paramètres de la bibliothèque"

    class Meta:
        verbose_name = "Paramètres de la bibliothèque"
        verbose_name_plural = "Paramètres de la bibliothèque"
