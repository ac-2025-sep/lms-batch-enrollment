from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from userops.api.permissions import IsStaffUser
from userops.services.meta_filter import METADATA_FILTER_KEYS, extract_org

CACHE_KEY = "userops:metadata_choices:v1"
CACHE_TTL_SECONDS = 300


def _course_org_run(course_key):
    org = getattr(course_key, "org", "")
    run = getattr(course_key, "run", "")
    if org and run:
        return str(org), str(run)

    course_id = str(course_key)
    if ":" in course_id:
        _, opaque_key = course_id.split(":", 1)
    else:
        opaque_key = course_id
    parts = opaque_key.split("+")
    guessed_org = parts[0] if parts else ""
    guessed_run = parts[2] if len(parts) > 2 else ""
    return guessed_org, guessed_run


class MetadataChoicesView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        cached = cache.get(CACHE_KEY)
        if cached is not None:
            return Response({"choices": cached})

        from common.djangoapps.student.models import UserProfile

        values_by_key = {key: set() for key in METADATA_FILTER_KEYS}
        profiles = UserProfile.objects.only("meta").all()

        for profile in profiles:
            org = extract_org(profile)
            for key in METADATA_FILTER_KEYS:
                raw_value = org.get(key)
                if raw_value is None:
                    continue
                value = str(raw_value).strip()
                if value:
                    values_by_key[key].add(value)

        choices = {key: sorted(values) for key, values in values_by_key.items()}
        cache.set(CACHE_KEY, choices, CACHE_TTL_SECONDS)
        return Response({"choices": choices})


class CourseChoicesView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

        courses = []
        for course in CourseOverview.objects.only("id", "display_name").all():
            org, run = _course_org_run(course.id)
            courses.append(
                {
                    "id": str(course.id),
                    "display_name": str(course.display_name or course.id),
                    "org": org,
                    "run": run,
                }
            )

        courses.sort(key=lambda item: (item["org"], item["display_name"], item["run"]))
        return Response({"courses": courses})
