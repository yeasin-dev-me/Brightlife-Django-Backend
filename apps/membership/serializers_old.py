from decimal import Decimal

from rest_framework import serializers

from .models import ApplicationStatusHistory, MembershipApplication, Nominee


class NomineeSerializer(serializers.ModelSerializer):
    """
    Serializer for Nominee model
    Validates share percentage and file uploads
    """

    class Meta:
        model = Nominee
        fields = [
            "id",
            "name",
            "relationship",
            "mobile_number",
            "nid_number",
            "date_of_birth",
            "share_percentage",
            "id_proof",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def validate_share_percentage(self, value):
        """Validate share percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Share percentage must be between 0 and 100"
            )
        return value

    def validate_id_proof(self, value):
        """Validate file size (max 5MB)"""
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5MB")
        return value


class MembershipApplicationSerializer(serializers.ModelSerializer):
    """
    Main serializer for membership application
    Handles nested nominees and file uploads
    """

    nominees = NomineeSerializer(many=True, required=False)
    age = serializers.IntegerField(read_only=True)
    proposal_number = serializers.CharField(read_only=True)

    class Meta:
        model = MembershipApplication
        fields = "__all__"
        read_only_fields = [
            "id",
            "proposal_number",
            "age",
            "created_at",
            "updated_at",
            "status",
        ]

    def validate(self, data):
        """
        Custom validation:
        1. Check if nominees' share percentages total 100%
        2. Validate date of birth (must be 18+ years old)
        3. Validate file sizes
        """
        # Parse nominees if it's a JSON string
        import json

        nominees_data = self.initial_data.get("nominees", [])
        if isinstance(nominees_data, str):
            try:
                nominees_data = json.loads(nominees_data)
            except json.JSONDecodeError:
                nominees_data = []

        # Store parsed nominees back to data
        if nominees_data:
            data["nominees"] = nominees_data

        # Validate nominees share percentage (only if nominees exist)
        if nominees_data:
            total_share = sum(
                Decimal(str(n.get("share_percentage", 0))) for n in nominees_data
            )
            if total_share != 100:
                raise serializers.ValidationError(
                    {
                        "nominees": f"Total share percentage must be 100%. Current total: {total_share}%"
                    }
                )

        # Validate age (18+ for individual, no restriction for family)
        from datetime import date

        dob = data.get("date_of_birth")
        if dob:
            today = date.today()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )

            if data.get("membership_type") == "individual" and age < 18:
                raise serializers.ValidationError(
                    {
                        "date_of_birth": "Applicant must be at least 18 years old for individual membership"
                    }
                )

        # Validate terms acceptance
        terms = data.get("terms_accepted")
        # Convert string "true"/"false" to boolean
        if isinstance(terms, str):
            terms = terms.lower() in ("true", "1", "yes")
            data["terms_accepted"] = terms

        if not terms:
            raise serializers.ValidationError(
                {"terms_accepted": "You must accept the terms and conditions"}
            )

        return data

    def validate_nid_number(self, value):
        """Check for duplicate NID"""
        if self.instance is None:  # Creating new record
            if MembershipApplication.objects.filter(nid_number=value).exists():
                raise serializers.ValidationError(
                    "An application with this NID number already exists"
                )
        return value

    def validate_photo(self, value):
        """Validate photo file"""
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Photo size cannot exceed 5MB")
        return value

    def create(self, validated_data):
        """
        Custom create method to handle nested nominees
        """
        nominees_data = validated_data.pop("nominees", [])

        # Create membership application
        application = MembershipApplication.objects.create(**validated_data)

        # Create associated nominees
        for nominee_data in nominees_data:
            Nominee.objects.create(application=application, **nominee_data)

        return application

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested nominees
        """
        nominees_data = validated_data.pop("nominees", None)

        # Update membership application fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update nominees if provided
        if nominees_data is not None:
            # Delete existing nominees
            instance.nominees.all().delete()

            # Create new nominees
            for nominee_data in nominees_data:
                Nominee.objects.create(application=instance, **nominee_data)

        return instance


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for status history tracking"""

    class Meta:
        model = ApplicationStatusHistory
        fields = "__all__"
        read_only_fields = ["timestamp"]


class MembershipApplicationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing applications (admin view)
    """

    nominees_count = serializers.SerializerMethodField()

    class Meta:
        model = MembershipApplication
        fields = [
            "id",
            "proposal_number",
            "first_name",
            "last_name",
            "membership_type",
            "status",
            "email",
            "mobile_number",
            "nominees_count",
            "created_at",
        ]

    def get_nominees_count(self, obj):
        return obj.nominees.count()
