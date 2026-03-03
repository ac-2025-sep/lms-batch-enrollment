from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from userops.api.permissions import IsStaffUser
from userops.services.meta_filter import extract_org

CACHE_KEY = "userops:metadata_choices:v2"
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
            return Response(cached)

        from common.djangoapps.student.models import UserProfile

        values_by_key = {}
        profiles = UserProfile.objects.only("meta").all()

        for profile in profiles:
            org = extract_org(profile)
            for key, raw_value in org.items():
                key_str = str(key).strip()
                if not key_str:
                    continue
                value = str(raw_value).strip()
                if not value:
                    continue
                values_by_key.setdefault(key_str, set()).add(value)

        keys = sorted(values_by_key.keys())
        choices = {key: sorted(values_by_key[key]) for key in keys}
        payload = {"choices": choices, "keys": keys}
        cache.set(CACHE_KEY, payload, CACHE_TTL_SECONDS)
        return Response(payload)


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
