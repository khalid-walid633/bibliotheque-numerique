
from django.urls import path

from .api_views import (
    DocumentListAPIView,
    DocumentDetailAPIView,
)

urlpatterns = [
    path(
        "documents/",
        DocumentListAPIView.as_view(),
        name="api_documents",
    ),

    path(
        "documents/<int:pk>/",
        DocumentDetailAPIView.as_view(),
        name="api_document_detail",
    ),
]
