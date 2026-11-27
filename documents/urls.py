from django.urls import path
from . import views

urlpatterns = [
    path("catalogue/", views.catalogue, name="catalogue"),
    path(
    "catalogue/<int:pk>/",
    views.detail_document,
    name="detail_document"
    ),
    path(
        "demander/",
        views.demander_emprunt,
        name="demander_emprunt"
    ),
    path(
        "mes-emprunts/",
        views.mes_emprunts,
        name="mes_emprunts"
    ),
    path(
        "gestion/",
        views.gestion_emprunts,
        name="gestion_emprunts"
    ),
    path(
    "tableau-bord/",
    views.tableau_bord,
    name="tableau_bord"
    ),
    path("mes-penalites/", views.mes_penalites, name="mes_penalites"),

    path(
    "parametres/",
    views.parametres_bibliotheque,
    name="parametres_bibliotheque"
    ),

]