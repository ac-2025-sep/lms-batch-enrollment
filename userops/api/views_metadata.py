from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from userops.api.permissions import IsStaffUser
from userops.services.meta_filter import METADATA_FILTER_KEYS, extract_org

CACHE_KEY = "userops:metadata_choices:v1"
CACHE_TTL_SECONDS = 300


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
