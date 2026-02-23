from django.urls import path

from .api.views import BulkEnrollByMetadataView, UserPreviewByMetadataView

urlpatterns = [
    path("users/preview", UserPreviewByMetadataView.as_view(), name="users-preview"),
    path("bulk-enroll/by-metadata", BulkEnrollByMetadataView.as_view(), name="bulk-enroll"),
]
