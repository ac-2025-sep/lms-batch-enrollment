from django.urls import path

from userops.api.views import BulkEnrollByMetadataView, UserPreviewByMetadataView

urlpatterns = [
    path("users/preview", UserPreviewByMetadataView.as_view(), name="userops-users-preview"),
    path(
        "bulk-enroll/by-metadata",
        BulkEnrollByMetadataView.as_view(),
        name="userops-bulk-enroll-by-metadata",
    ),
]
