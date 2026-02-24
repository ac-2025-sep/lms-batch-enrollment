from django.urls import path

from .api.views import BulkEnrollByMetadataView, UserPreviewByMetadataView
from .api.views_metadata import CourseChoicesView, MetadataChoicesView

urlpatterns = [
    path("users/preview", UserPreviewByMetadataView.as_view(), name="users-preview"),
    path("bulk-enroll/by-metadata", BulkEnrollByMetadataView.as_view(), name="bulk-enroll"),
    path("metadata/choices", MetadataChoicesView.as_view(), name="metadata-choices"),
    path("courses", CourseChoicesView.as_view(), name="course-choices"),
]
