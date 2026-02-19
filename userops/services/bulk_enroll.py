from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate


def forward_to_bulk_enroll(*, user, courses, identifiers, cohorts, action, auto_enroll, email_students):
    """Forward to Open edX BulkEnrollView to reuse platform enrollment logic."""
    # Kept as an internal DRF call so we avoid external HTTP networking.
    from lms.djangoapps.bulk_enroll.views import BulkEnrollView

    payload = {
        "courses": ",".join(courses),
        "identifiers": ",".join(identifiers),
        "action": action,
        "auto_enroll": auto_enroll,
        "email_students": email_students,
    }
    if cohorts:
        payload["cohorts"] = ",".join(cohorts)

    factory = APIRequestFactory()
    request = factory.post("/api/bulk_enroll/v1/bulk_enroll/", payload, format="json")
    force_authenticate(request, user=user)

    response = BulkEnrollView.as_view()(request)
    if hasattr(response, "render"):
        response.render()

    body = response.data if isinstance(response, Response) else getattr(response, "data", None)
    return response.status_code, body
