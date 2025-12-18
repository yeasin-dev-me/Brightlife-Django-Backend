from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import AgentApplication


class AgentApplicationSerializer(serializers.ModelSerializer):
    """Serializer used for create/detail operations."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = AgentApplication
        fields = [
            "id",
            "agent_id",
            "applicant_role",
            "fm_name",
            "role_code",
            "dgm_name",
            "dgm_code",
            "gm_name",
            "gm_code",
            "full_name",
            "email",
            "phone",
            "address",
            "guardian_name",
            "mother_name",
            "present_address",
            "permanent_address",
            "dob",
            "birth_place",
            "nid_number",
            "bank_account_number",
            "bank_name",
            "bank_branch_name",
            "applicant_photo",
            "nid_document",
            "education_certificate",
            "agree_terms",
            "status",
            "submitted_at",
            "updated_at",
            "password",
            "confirm_password",
        ]
        read_only_fields = ["status", "submitted_at", "updated_at"]
        extra_kwargs = {
            "agent_id": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "fm_name": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "role_code": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "dgm_name": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "dgm_code": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "gm_name": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "gm_code": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.pop("confirm_password", None)
        if confirm_password is None:
            raise serializers.ValidationError(
                {"confirm_password": "Please confirm your password."}
            )
        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        sanitized_phone = attrs.get("phone", "")
        attrs["phone"] = sanitized_phone.strip()

        if not attrs.get("agree_terms"):
            raise serializers.ValidationError(
                {"agree_terms": "You must accept the terms and conditions."}
            )

        return attrs

    def create(self, validated_data):
        raw_password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(raw_password)
        return super().create(validated_data)


class AgentApplicationListSerializer(serializers.ModelSerializer):
    """Serializer optimized for admin listings."""

    class Meta:
        model = AgentApplication
        fields = [
            "id",
            "agent_id",
            "full_name",
            "applicant_role",
            "status",
            "submitted_at",
        ]
