from rest_framework import serializers
from .models import PaymentProof
import re


class PaymentProofSerializer(serializers.ModelSerializer):
    """Serializer for payment proof submission"""
    
    class Meta:
        model = PaymentProof
        fields = [
            'id',
            'transaction_id',
            'payment_method',
            'amount',
            'payer_name',
            'payer_contact',
            'screenshot',
            'notes',
            'status',
            'submitted_at',
            'verified_at',
            'rejection_reason'
        ]
        read_only_fields = [
            'id', 
            'status', 
            'submitted_at', 
            'verified_at', 
            'rejection_reason'
        ]
    
    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_payer_contact(self, value):
        """Validate phone number format"""
        # Allow numbers, spaces, +, -, ()
        if not re.match(r'^[0-9+\-\s()]+$', value):
            raise serializers.ValidationError("Invalid phone number format. Use only numbers and +, -, (, )")
        
        # Remove non-digit characters for length check
        digits_only = re.sub(r'[^0-9]', '', value)
        if len(digits_only) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits")
        
        return value
    
    def validate_screenshot(self, value):
        """Validate screenshot file"""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("File size must be less than 5MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Only JPEG, PNG, and PDF files are allowed"
                )
        
        return value
    
    def validate_transaction_id(self, value):
        """Validate transaction ID format and uniqueness"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Transaction ID must be at least 5 characters long"
            )
        return value.strip()


class PaymentProofListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    
    class Meta:
        model = PaymentProof
        fields = [
            'id',
            'transaction_id',
            'payment_method',
            'amount',
            'payer_name',
            'status',
            'submitted_at'
        ]


class PaymentProofAdminSerializer(serializers.ModelSerializer):
    """Full serializer for admin operations"""
    verified_by_username = serializers.CharField(
        source='verified_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = PaymentProof
        fields = '__all__'
        read_only_fields = ['id', 'submitted_at', 'updated_at']
