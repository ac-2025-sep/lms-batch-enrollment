from rest_framework import serializers


def build_filters_field():
    return serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField(allow_blank=False),
            allow_empty=False,
        ),
        required=True,
    )


class MetadataFiltersMixin:
    def validate_filters(self, value):
        if not value:
            raise serializers.ValidationError("At least one filter must be provided.")

        normalized = {}
        for key, raw_values in value.items():
            key_str = str(key).strip()
            if not key_str:
                raise serializers.ValidationError("Filter keys must be non-empty strings.")

            if not isinstance(raw_values, list):
                raise serializers.ValidationError({key_str: "Expected an array of strings."})
            if not raw_values:
                raise serializers.ValidationError({key_str: "Filter arrays must not be empty."})

            values = []
            for raw in raw_values:
                value_str = str(raw).strip()
                if not value_str:
                    raise serializers.ValidationError({key_str: "Filter values must be non-empty strings."})
                values.append(value_str)

            normalized[key_str] = values
        return normalized


class PreviewRequestSerializer(MetadataFiltersMixin, serializers.Serializer):
    filters = build_filters_field()


class BulkEnrollByMetadataSerializer(MetadataFiltersMixin, serializers.Serializer):
    filters = build_filters_field()
    courses = serializers.JSONField(required=True)
    cohorts = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_empty=True,
    )
    action = serializers.ChoiceField(choices=["enroll", "unenroll"], default="enroll")
    auto_enroll = serializers.BooleanField(default=True)
    email_students = serializers.BooleanField(default=False)
    selected_identifiers = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=False,
        allow_empty=True,
    )

    def validate_selected_identifiers(self, value):
        normalized = []
        for raw in value:
            identifier = str(raw).strip()
            if identifier:
                normalized.append(identifier)
        return normalized

    def validate_courses(self, value):
        if isinstance(value, str):
            candidates = value.split(",")
        elif isinstance(value, list):
            candidates = value
        else:
            raise serializers.ValidationError("courses must be a list of course keys or comma-separated string.")

        normalized = []
        for raw in candidates:
            course = str(raw).strip()
            if course:
                normalized.append(course)

        if not normalized:
            raise serializers.ValidationError("At least one course must be provided.")
        return normalized

    def validate(self, attrs):
        cohorts = attrs.get("cohorts")
        if cohorts is not None and len(cohorts) not in (0, len(attrs["courses"])):
            raise serializers.ValidationError(
                {"cohorts": "If provided, cohorts count must match courses count."}
            )
        return attrs
