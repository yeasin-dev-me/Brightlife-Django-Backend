from decimal import Decimal

from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from .models import (
    ApplicationStatusHistory,
    MedicalRecord,
    MembershipApplication,
    Nominee,
)


class MemberLoginSerializer(serializers.Serializer):
    """
    Serializer for member login authentication
    Uses Proposal Number + Birth Year for validation
    """

    proposalNo = serializers.CharField(
        max_length=50,
        required=True,
        help_text="Member's Proposal Number (e.g., BL-202512-0001 or BLBD-1234567890)",
    )
    birthYear = serializers.IntegerField(
        required=True,
        min_value=1900,
        max_value=2100,
        help_text="Member's birth year (4 digits, e.g., 1990)",
    )

    def validate_proposalNo(self, value):
        """Normalize proposal number"""
        return value.strip().upper()

    def validate_birthYear(self, value):
        """Validate birth year is reasonable"""
        from datetime import datetime

        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("Birth year cannot be in the future")
        if value < 1900:
            raise serializers.ValidationError("Birth year must be after 1900")
        return value


class MemberProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for returning member profile data after login
    """

    class Meta:
        model = MembershipApplication
        fields = [
            "id",
            "proposal_no",
            "proposal_number",
            "name_english",
            "name_bangla",
            "email",
            "mobile",
            "membership_type",
            "status",
            "valid_until",
            "dob",
            "gender",
            "blood_group",
            "present_address",
            "created_at",
            "photo",
        ]
        read_only_fields = fields


class NomineeSerializer(serializers.ModelSerializer):
    """
    Serializer for Nominee model matching frontend structure
    """

    class Meta:
        model = Nominee
        fields = [
            "name",
            "relationship",
            "relation",
            "share",
            "age",
            "photo",
            "id_proof",
        ]
        extra_kwargs = {
            "relation": {"required": False},
            "relationship": {"required": False},
            "photo": {"required": False, "allow_null": True},
            "id_proof": {"required": False, "allow_null": True},
        }

    def validate_share(self, value):
        """Validate share percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Share percentage must be between 0 and 100"
            )
        return value

    def validate(self, data):
        """Normalize relationship from user input"""
        # Normalize relationship if relation is provided
        if "relation" in data:
            relation = data["relation"].lower().strip()
            mapping = {
                "son": "child",
                "daughter": "child",
                "wife": "spouse",
                "husband": "spouse",
                "father": "father",
                "mother": "mother",
                "brother": "sibling",
                "sister": "sibling",
            }
            data["relationship"] = mapping.get(relation, "child")
        return data


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for medical record files"""

    class Meta:
        model = MedicalRecord
        fields = ["file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class MembershipApplicationSerializer(serializers.ModelSerializer):
    """
    Main serializer for membership application
    Handles field mapping from frontend to backend
    """

    nominees = NomineeSerializer(many=True, required=False)
    medical_records = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )

    class Meta:
        model = MembershipApplication
        fields = [
            # Proposal info
            "proposal_no",
            "fo_code",
            "fo_name",
            # Personal info
            "membership_type",
            "gender",
            "name_bangla",
            "name_english",
            "father_name",
            "mother_name",
            "spouse_name",
            "mobile",
            "email",
            "photo",
            "dob",
            "age",
            "nationality",
            "age_proof",
            "age_proof_doc",
            "driving_license",
            "license_doc",
            "marital_status",
            "education",
            "professional_qualifications",
            "occupation",
            "organization_details",
            "daily_work",
            "monthly_income",
            "income_source",
            # Address
            "present_address",
            "permanent_address",
            # Nominees
            "nominees",
            # Physical measurements
            "weight",
            "height",
            "blood_group",
            "chest",
            "surgery_details",
            "medical_records",
            # Terms
            "accept_terms",
            # Meta
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["proposal_no", "age", "created_at", "updated_at", "status"]

    def validate_membership_type(self, value):
        """Map frontend membership types to backend choices"""
        mapping = {
            "silver": "individual",
            "bronze": "individual",
            "gold": "family",
            "executive": "corporate",
        }
        return mapping.get(value.lower(), value)

    def validate_marital_status(self, value):
        """Map frontend marital status to backend choices"""
        mapping = {
            "unmarried": "single",
            "married": "married",
            "divorced": "divorced",
            "others": "widowed",
        }
        return mapping.get(value.lower(), value)

    def validate(self, data):
        """
        Custom validation:
        1. Check if nominees' shares total 100%
        2. Validate terms acceptance
        """
        # Validate nominees share percentage (only if nominees exist)
        nominees_data = data.get("nominees", [])
        if nominees_data:
            total_share = sum(int(n.get("share", 0)) for n in nominees_data)
            if total_share != 100:
                raise serializers.ValidationError(
                    {
                        "nominees": f"Total share must equal 100%. Current total: {total_share}%"
                    }
                )

        # Validate terms acceptance
        accept_terms = data.get("accept_terms")
        if isinstance(accept_terms, str):
            accept_terms = accept_terms.lower() in ("true", "1", "yes")
            data["accept_terms"] = accept_terms

        if not accept_terms:
            raise serializers.ValidationError(
                {"accept_terms": "You must accept the terms and conditions"}
            )

        return data

    def create(self, validated_data):
        """Create application with nominees and medical records"""
        nominees_data = validated_data.pop("nominees", [])
        medical_records = validated_data.pop("medical_records", [])

        # Create application
        application = MembershipApplication.objects.create(**validated_data)

        # Create nominees
        for nominee_data in nominees_data:
            Nominee.objects.create(application=application, **nominee_data)

        # Create medical records
        for file in medical_records:
            MedicalRecord.objects.create(application=application, file=file)

        return application


class MembershipApplicationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""

    class Meta:
        model = MembershipApplication
        fields = [
            "id",
            "proposal_no",
            "name_english",
            "membership_type",
            "mobile",
            "email",
            "status",
            "created_at",
        ]


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for status history"""

    class Meta:
        model = ApplicationStatusHistory
        fields = "__all__"
