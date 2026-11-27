from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Utilisateur


@login_required
def liste_abonnes(request):

    if not (
        request.user.is_superuser
        or request.user.role in [
            Utilisateur.Role.ADMIN,
            Utilisateur.Role.BIBLIOTHECAIRE
        ]
    ):
        return HttpResponseForbidden(
            "Accès réservé à l'administrateur et au bibliothécaire."
        )

    abonnes = Utilisateur.objects.filter(
        role=Utilisateur.Role.ABONNE
    ).order_by("username")

    return render(
        request,
        "users/liste_abonnes.html",
        {
            "abonnes": abonnes
        }
    )