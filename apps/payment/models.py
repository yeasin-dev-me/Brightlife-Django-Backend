from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone
import uuid


class PaymentProof(models.Model):
    """Model for storing payment proof submissions"""
    
    PAYMENT_METHOD_CHOICES = [
        ('touch-n-go', 'Touch n Go eWallet'),
        ('bkash', 'Bkash'),
        ('bank-transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Transaction/Reference ID from payment'
    )
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        help_text='Payment method used'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text='Payment amount'
    )
    payer_name = models.CharField(
        max_length=200,
        help_text='Name of person who made payment'
    )
    payer_contact = models.CharField(
        max_length=50,
        help_text='Contact number of payer'
    )
    screenshot = models.ImageField(
        upload_to='payment_proofs/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        help_text='Payment screenshot/receipt (max 5MB)'
    )
    notes = models.TextField(
        max_length=500, 
        blank=True,
        help_text='Additional notes or comments'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text='Verification status'
    )
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Timestamp when payment was verified'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        help_text='Admin user who verified the payment'
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text='Reason for rejection (if rejected)'
    )
    
    # Optional: Link to membership application
    membership_application = models.ForeignKey(
        'membership.MembershipApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_proofs',
        help_text='Associated membership application'
    )
    
    # Tracking
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of submitter'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='Browser user agent'
    )
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Payment Proof'
        verbose_name_plural = 'Payment Proofs'
        indexes = [
            models.Index(fields=['-submitted_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.payer_name} ({self.status})"
    
    def verify(self, user=None):
        """Mark payment as verified"""
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.verified_by = user
        self.save()
    
    def reject(self, reason, user=None):
        """Mark payment as rejected"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()
