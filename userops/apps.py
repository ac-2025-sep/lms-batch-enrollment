from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginURLs


class UserOpsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "userops"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "userops",
                PluginURLs.REGEX: r"^",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        }
    }
