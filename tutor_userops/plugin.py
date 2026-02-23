"""Tutor plugin registration for userops."""

from pathlib import Path

from tutor import hooks

PLUGIN_ROOT = Path(__file__).resolve().parent
PATCHES_ROOT = PLUGIN_ROOT / "patches"


def _read_patch(name: str) -> str:
    return (PATCHES_ROOT / name).read_text(encoding="utf-8").strip()


hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "openedx-lms-common-settings",
            _read_patch("openedx-lms-common-settings"),
        ),
        (
            "openedx-lms-env-features",
            _read_patch("openedx-lms-env-features"),
        ),
        (
            "openedx-dockerfile-post-python-requirements",
            "RUN pip install /openedx/plugins/userops",
        ),
    ]
)

hooks.Filters.IMAGES_BUILD_REQUIRED.add_item(("plugins/userops", "."))
