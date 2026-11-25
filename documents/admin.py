from .models import (
    Categorie,
    Document,
    Exemplaire,
    Emprunt,
    Penalite,
    ParametresBibliotheque,
)
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .services import valider_emprunt, enregistrer_retour


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)


class ExemplaireInline(admin.TabularInline):
    model = Exemplaire
    extra = 1


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'titre',
        'auteur',
        'type_document',
        'annee_publication',
        'categorie',
    )

    list_filter = (
        'type_document',
        'categorie',
        'annee_publication',
    )

    search_fields = ('titre', 'auteur', 'isbn')
    inlines = [ExemplaireInline]


@admin.register(Exemplaire)
class ExemplaireAdmin(admin.ModelAdmin):
    list_display = (
        'code_inventaire',
        'document',
        'etat',
        'emplacement',
    )

    list_filter = ('etat',)
    search_fields = ('code_inventaire', 'document__titre')


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'abonne',
        'exemplaire',
        'date_demande',
        'date_limite',
        'statut',
        'bibliothecaire',
    )

    list_filter = ('statut', 'date_demande')

    search_fields = (
        'abonne__username',
        'exemplaire__code_inventaire',
    )

    readonly_fields = ('date_demande',)

    actions = [
        'valider_demandes',
        'enregistrer_retours',
    ]

    @admin.action(description="Valider les demandes sélectionnées")
    def valider_demandes(self, request, queryset):
        validees = 0
        erreurs = []

        for emprunt in queryset:
            try:
                valider_emprunt(
                    emprunt_id=emprunt.pk,
                    bibliothecaire=request.user,
                    duree_jours=None,
                )
                validees += 1

            except ValidationError as erreur:
                erreurs.append(
                    f"Emprunt #{emprunt.pk} : {erreur}"
                )

        if validees:
            self.message_user(
                request,
                f"{validees} emprunt(s) validé(s).",
                messages.SUCCESS,
            )

        for erreur in erreurs:
            self.message_user(
                request,
                erreur,
                messages.ERROR,
            )

    @admin.action(
        description="Enregistrer le retour des emprunts sélectionnés"
    )
    def enregistrer_retours(self, request, queryset):
        retournes = 0
        erreurs = []

        for emprunt in queryset:
            try:
                enregistrer_retour(
                    emprunt_id=emprunt.pk,
                    bibliothecaire=request.user,
                )
                retournes += 1

            except (ValidationError, Emprunt.DoesNotExist) as erreur:
                erreurs.append(
                    f"Emprunt #{emprunt.pk} : {erreur}"
                )

        if retournes:
            self.message_user(
                request,
                f"{retournes} retour(s) enregistré(s).",
                messages.SUCCESS,
            )

        for erreur in erreurs:
            self.message_user(
                request,
                erreur,
                messages.ERROR,
            )
@admin.register(Penalite)
class PenaliteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "emprunt",
        "jours_retard",
        "montant",
        "date_creation",
    )

    search_fields = (
        "emprunt__abonne__username",
    )

    list_filter = ("date_creation",)

    readonly_fields = (
        "emprunt",
        "jours_retard",
        "montant",
        "date_creation",
    )

@admin.register(ParametresBibliotheque)
class ParametresBibliothequeAdmin(admin.ModelAdmin):

    list_display = (
        "duree_emprunt",
        "tarif_penalite",
    )

    fields = (
        "duree_emprunt",
        "tarif_penalite",
    )

    def has_add_permission(self, request):
        return not ParametresBibliotheque.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
