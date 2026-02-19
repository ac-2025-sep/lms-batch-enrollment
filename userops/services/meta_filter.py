import json
from typing import Any

def _normalize(value: Any) -> str:
    return str(value).strip().casefold()


def parse_profile_meta(meta_raw: str | None) -> dict:
    if not meta_raw:
        return {}
    try:
        parsed = json.loads(meta_raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def extract_org(profile) -> dict:
    parsed = parse_profile_meta(profile.meta)
    org = parsed.get("org", {})
    return org if isinstance(org, dict) else {}


def user_matches_filters(profile, filters: dict[str, str]) -> bool:
    org = extract_org(profile)
    for key, expected_value in filters.items():
        if key not in org:
            return False
        if _normalize(org.get(key)) != _normalize(expected_value):
            return False
    return True


def get_matched_profiles(filters: dict[str, str]):
    from common.djangoapps.student.models import UserProfile

    profiles = UserProfile.objects.select_related("user").all()
    return [profile for profile in profiles if user_matches_filters(profile, filters)]
