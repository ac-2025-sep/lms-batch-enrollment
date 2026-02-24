from rest_framework import serializers


class PreviewRequestSerializer(serializers.Serializer):
    filters = serializers.DictField(child=serializers.CharField(allow_blank=False), required=True)


class BulkEnrollByMetadataSerializer(serializers.Serializer):
    filters = serializers.DictField(child=serializers.CharField(allow_blank=False), required=True)
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

    def validate_filters(self, value):
        if not value:
            raise serializers.ValidationError("At least one filter must be provided.")
        normalized = {}
        for key, raw in value.items():
            key_str = str(key).strip()
            if not key_str:
                raise serializers.ValidationError("Filter keys must be non-empty strings.")
            val_str = str(raw).strip()
            if not val_str:
                raise serializers.ValidationError(f"Filter value for '{key_str}' must be non-empty.")
            normalized[key_str] = val_str
        return normalized

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
