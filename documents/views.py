from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from .models import Exemplaire, Emprunt
from .services import valider_emprunt
from django.core.paginator import Paginator
from .models import Document, Categorie
from django.db.models import Count, Q
from users.models import Utilisateur

@login_required
def demander_emprunt(request):
    if request.method == "POST":
        exemplaire_id = request.POST.get("exemplaire")

        try:
            exemplaire = Exemplaire.objects.get(
                pk=exemplaire_id,
                etat=Exemplaire.Etat.DISPONIBLE
            )

            Emprunt.objects.create(
                abonne=request.user,
                exemplaire=exemplaire,
                statut=Emprunt.Statut.DEMANDEE
            )

            messages.success(
                request,
                "Votre demande d'emprunt a été enregistrée."
            )

            return redirect("demander_emprunt")

        except Exemplaire.DoesNotExist:
            messages.error(
                request,
                "Exemplaire introuvable ou indisponible."
            )

    exemplaires = Exemplaire.objects.filter(
        etat=Exemplaire.Etat.DISPONIBLE
    ).select_related("document")

    return render(
        request,
        "documents/demander_emprunt.html",
        {"exemplaires": exemplaires}
    )


@login_required
def mes_emprunts(request):
    emprunts = Emprunt.objects.filter(
        abonne=request.user
    ).select_related("exemplaire__document")

    return render(
        request,
        "documents/mes_emprunts.html",
        {"emprunts": emprunts}
    )

@login_required
def gestion_emprunts(request):
    # Réserver cette page au bibliothécaire et à l'administrateur
    if not (
    request.user.is_superuser
    or request.user.role in [
        Utilisateur.Role.ADMIN,
        Utilisateur.Role.BIBLIOTHECAIRE
    ]
    ):
        return HttpResponseForbidden(
            "Accès réservé au bibliothécaire."
        )

    if request.method == "POST":
        emprunt_id = request.POST.get("emprunt_id")
        action = request.POST.get("action")

        try:
            emprunt = Emprunt.objects.get(
                pk=emprunt_id,
                statut=Emprunt.Statut.DEMANDEE
            )

            if action == "accepter":
                valider_emprunt(
                    emprunt_id=emprunt.pk,
                    bibliothecaire=request.user,
                    duree_jours=14
                )
                messages.success(
                    request,
                    f"La demande #{emprunt.pk} a été acceptée."
                )

            elif action == "refuser":
                emprunt.statut = Emprunt.Statut.REFUSEE
                emprunt.bibliothecaire = request.user
                emprunt.save(
                    update_fields=["statut", "bibliothecaire"]
                )
                messages.success(
                    request,
                    f"La demande #{emprunt.pk} a été refusée."
                )

            else:
                messages.error(request, "Action invalide.")

        except Emprunt.DoesNotExist:
            messages.error(
                request,
                "Demande introuvable ou déjà traitée."
            )

        except ValidationError as erreur:
            messages.error(request, str(erreur))

        return redirect("gestion_emprunts")

    demandes = Emprunt.objects.filter(
        statut=Emprunt.Statut.DEMANDEE
    ).select_related(
        "abonne",
        "exemplaire__document"
    ).order_by("date_demande")

    return render(
        request,
        "documents/gestion_emprunts.html",
        {"demandes": demandes}
    )

def catalogue(request):
    documents = Document.objects.select_related(
        "categorie"
    ).all().order_by("titre")

    recherche = request.GET.get("q", "").strip()
    categorie_id = request.GET.get("categorie", "")

    if recherche:
        documents = documents.filter(
            titre__icontains=recherche
        ) | documents.filter(
            auteur__icontains=recherche
        ) | documents.filter(
            isbn__icontains=recherche
        )

    if categorie_id:
        documents = documents.filter(
            categorie_id=categorie_id
        )

    categories = Categorie.objects.all().order_by("nom")

    paginator = Paginator(documents, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "documents/catalogue.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "recherche": recherche,
            "categorie_selectionnee": categorie_id,
        }
    )


def detail_document(request, pk):
    document = Document.objects.select_related(
        "categorie"
    ).get(pk=pk)

    exemplaires = Exemplaire.objects.filter(
        document=document
    )

    disponibles = exemplaires.filter(
        etat=Exemplaire.Etat.DISPONIBLE
    ).count()

    return render(
        request,
        "documents/detail_document.html",
        {
            "document": document,
            "exemplaires": exemplaires,
            "disponibles": disponibles,
        }
    )
@login_required
def tableau_bord(request):

    if not (
    request.user.is_superuser
    or request.user.role in [
        Utilisateur.Role.ADMIN,
        Utilisateur.Role.BIBLIOTHECAIRE
    ]
):
        return HttpResponseForbidden(
            "Accès réservé au bibliothécaire."
        )

    statistiques = {
        "documents": Document.objects.count(),
        "exemplaires": Exemplaire.objects.count(),
        "disponibles": Exemplaire.objects.filter(
            etat=Exemplaire.Etat.DISPONIBLE
        ).count(),
        "empruntes": Exemplaire.objects.filter(
            etat=Exemplaire.Etat.EMPRUNTE
        ).count(),
        "demandes": Emprunt.objects.filter(
            statut=Emprunt.Statut.DEMANDEE
        ).count(),
        "emprunts_actifs": Emprunt.objects.filter(
            statut=Emprunt.Statut.EN_COURS
        ).count(),
        "abonnes": Utilisateur.objects.filter(
            role="ABONNE",
            is_active=True
        ).count(),
    }

    dernieres_demandes = Emprunt.objects.select_related(
        "abonne",
        "exemplaire__document"
    ).order_by("-date_demande")[:5]

    return render(
        request,
        "documents/tableau_bord.html",
        {
            "statistiques": statistiques,
            "dernieres_demandes": dernieres_demandes,
        }
    )