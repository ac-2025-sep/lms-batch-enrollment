import json
from typing import Any

METADATA_FILTER_KEYS = [
    "dealer_id",
    "champion_name",
    "champion_mobile",
    "dealer_name",
    "city",
    "state",
    "dealer_category",
    "cluster",
    "asm_1",
    "asm_2",
    "role",
    "department",
    "brand",
]


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


def user_matches_filters(profile, filters: dict[str, list[str]]) -> bool:
    org = extract_org(profile)
    normalized_user_meta = {key: _normalize(value) for key, value in org.items()}

    for key, allowed_values in filters.items():
        normalized_allowed_values = [_normalize(value) for value in allowed_values]
        user_value = normalized_user_meta.get(key)
        if user_value not in normalized_allowed_values:
            return False
    return True


def get_matched_profiles(filters: dict[str, list[str]]):
    from common.djangoapps.student.models import UserProfile

    profiles = UserProfile.objects.select_related("user").all()
    return [profile for profile in profiles if user_matches_filters(profile, filters)]
