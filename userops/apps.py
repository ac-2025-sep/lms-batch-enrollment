from django.apps import AppConfig

from openedx.core.djangoapps.plugins.constants import PluginURLs


class UserOpsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "userops"

    plugin_app = {
        PluginURLs.CONFIG: {
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "userops",
                PluginURLs.REGEX: r"^api/userops/v1/",
                PluginURLs.RELATIVE_PATH: "urls",
            }
        }
    }
