
from django.urls import path
from . import views

urlpatterns = [
    path(
        "abonnes/",
        views.liste_abonnes,
        name="liste_abonnes"
    ),
]
