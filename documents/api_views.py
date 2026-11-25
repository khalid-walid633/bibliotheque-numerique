
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import Document
from .serializers import DocumentSerializer


class CataloguePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class DocumentListAPIView(generics.ListAPIView):

    queryset = Document.objects.select_related(
        "categorie"
    ).all().order_by("id")

    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
    pagination_class = CataloguePagination

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "titre",
        "auteur",
        "isbn",
        "categorie__nom",
    ]

    ordering_fields = [
        "titre",
        "annee_publication",
    ]


class DocumentDetailAPIView(generics.RetrieveAPIView):

    queryset = Document.objects.select_related(
        "categorie"
    )

    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
