import json
from dataclasses import dataclass

from userops.services.meta_filter import parse_profile_meta, user_matches_filters


@dataclass
class DummyProfile:
    meta: str


def test_parse_profile_meta_invalid_json_returns_empty_dict():
    assert parse_profile_meta("not-json") == {}


def test_user_matches_filters_case_insensitive_and_trimmed():
    profile = DummyProfile(
        meta=json.dumps({"org": {"cluster": " North 1 ", "asm_1": "AsmX"}})
    )
    assert user_matches_filters(profile, {"cluster": "north 1", "asm_1": "asmx"})


def test_user_matches_filters_missing_key_fails():
    profile = DummyProfile(meta=json.dumps({"org": {"cluster": "NORTH"}}))
    assert not user_matches_filters(profile, {"cluster": "north", "asm_1": "asm1"})
