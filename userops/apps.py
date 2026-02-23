from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginURLs


class UserOpsConfig(AppConfig):
    name = "userops"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": [
                {
                    "namespace": "userops_api",
                    "regex": r"^api/userops/v1/",
                    "relative_path": "urls_api",
                },
                {
                    "namespace": "userops_ui",
                    "regex": r"^userops/",
                    "relative_path": "urls_ui",
                },
            ]
        }
    }
