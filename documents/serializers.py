
from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):

    categorie = serializers.CharField(
        source="categorie.nom",
        read_only=True
    )

    class Meta:
        model = Document

        fields = [
            "id",
            "titre",
            "auteur",
            "isbn",
            "annee_publication",
            "type_document",
            "description",
            "categorie",
        ]
