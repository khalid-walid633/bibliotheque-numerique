
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Emprunt,
    Exemplaire,
    Penalite,
    ParametresBibliotheque,
)


def obtenir_parametres():
    parametres, created = ParametresBibliotheque.objects.get_or_create(
        pk=1,
        defaults={
            "duree_emprunt": 14,
            "tarif_penalite": Decimal("2.00"),
        }
    )
    return parametres


@transaction.atomic
def valider_emprunt(emprunt_id, bibliothecaire, duree_jours=None):

    parametres = obtenir_parametres()

    if duree_jours is None:
        duree_jours = parametres.duree_emprunt

    if duree_jours <= 0:
        raise ValidationError(
            "La durée de l'emprunt doit être positive."
        )

    emprunt = Emprunt.objects.select_for_update().get(
        pk=emprunt_id
    )

    if emprunt.statut != Emprunt.Statut.DEMANDEE:
        raise ValidationError(
            "Cette demande n'est pas en attente de validation."
        )

    exemplaire = Exemplaire.objects.select_for_update().get(
        pk=emprunt.exemplaire_id
    )

    if exemplaire.etat != Exemplaire.Etat.DISPONIBLE:
        raise ValidationError(
            "Cet exemplaire n'est pas disponible."
        )

    emprunt_actif = Emprunt.objects.filter(
        exemplaire=exemplaire,
        statut=Emprunt.Statut.EN_COURS
    ).exists()

    if emprunt_actif:
        raise ValidationError(
            "Cet exemplaire possède déjà un emprunt actif."
        )

    maintenant = timezone.now()
    date_limite = maintenant.date() + timedelta(
        days=duree_jours
    )

    emprunt.statut = Emprunt.Statut.EN_COURS
    emprunt.date_emprunt = maintenant
    emprunt.date_limite = date_limite
    emprunt.duree_appliquee = duree_jours
    emprunt.bibliothecaire = bibliothecaire

    emprunt.save(
        update_fields=[
            "statut",
            "date_emprunt",
            "date_limite",
            "duree_appliquee",
            "bibliothecaire",
        ]
    )

    exemplaire.etat = Exemplaire.Etat.EMPRUNTE
    exemplaire.save(update_fields=["etat"])

    return emprunt


@transaction.atomic
def enregistrer_retour(emprunt_id, bibliothecaire):

    emprunt = Emprunt.objects.select_for_update().get(
        pk=emprunt_id
    )

    if emprunt.statut != Emprunt.Statut.EN_COURS:
        raise ValidationError(
            "Seul un emprunt en cours peut être retourné."
        )

    exemplaire = Exemplaire.objects.select_for_update().get(
        pk=emprunt.exemplaire_id
    )

    date_retour = timezone.localdate()

    emprunt.statut = Emprunt.Statut.TERMINEE
    emprunt.date_retour = date_retour
    emprunt.bibliothecaire = bibliothecaire

    emprunt.save(
        update_fields=[
            "statut",
            "date_retour",
            "bibliothecaire",
        ]
    )

    exemplaire.etat = Exemplaire.Etat.DISPONIBLE
    exemplaire.save(update_fields=["etat"])

    if emprunt.date_limite:
        jours_retard = max(
            0,
            (date_retour - emprunt.date_limite).days
        )

        if jours_retard > 0:
            parametres = obtenir_parametres()

            montant = (
                Decimal(jours_retard)
                * parametres.tarif_penalite
            )

            Penalite.objects.update_or_create(
                emprunt=emprunt,
                defaults={
                    "jours_retard": jours_retard,
                    "montant": montant,
                }
            )

    return emprunt
