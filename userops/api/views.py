from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from userops.api.permissions import IsStaffUser
from userops.api.serializers import BulkEnrollByMetadataSerializer, PreviewRequestSerializer
from userops.services.bulk_enroll import forward_to_bulk_enroll
from userops.services.meta_filter import extract_org, get_matched_profiles


class UserPreviewByMetadataView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = PreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data["filters"]
        limit = serializer.validated_data["limit"]

        matched_profiles = get_matched_profiles(filters)
        sample = []
        for profile in matched_profiles[:limit]:
            sample.append(
                {
                    "username": profile.user.username,
                    "email": profile.user.email,
                    "org": extract_org(profile),
                }
            )

        return Response({"count": len(matched_profiles), "sample": sample})


class BulkEnrollByMetadataView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = BulkEnrollByMetadataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        matched_profiles = get_matched_profiles(data["filters"])

        identifiers = []
        skipped_no_email = 0
        for profile in matched_profiles:
            email = (profile.user.email or "").strip()
            if email:
                identifiers.append(email)
            else:
                skipped_no_email += 1

        upstream_status = status.HTTP_400_BAD_REQUEST
        upstream_body = {"detail": "No matching users with email found."}

        if identifiers:
            upstream_status, upstream_body = forward_to_bulk_enroll(
                user=request.user,
                courses=data["courses"],
                identifiers=identifiers,
                cohorts=data.get("cohorts") or [],
                action=data["action"],
                auto_enroll=data["auto_enroll"],
                email_students=data["email_students"],
            )

        response_payload = {
            "matched_users": len(matched_profiles),
            "used_identifiers": len(identifiers),
            "skipped_no_email": skipped_no_email,
            "upstream_status": upstream_status,
            "upstream_body": upstream_body,
        }
        return Response(response_payload, status=upstream_status)
