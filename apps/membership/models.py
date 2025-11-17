from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
import uuid


class MembershipApplication(models.Model):
    """
    Main membership application model matching frontend MembershipFormData interface
    """

    # Auto-generated fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Step 1: Personal Information
    MEMBERSHIP_TYPE_CHOICES = [
        ('individual', 'Individual Membership'),
        ('family', 'Family Membership'),
        ('corporate', 'Corporate Membership'),
    ]
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPE_CHOICES)

    # Name fields
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)

    # Date of birth and calculated age
    date_of_birth = models.DateField()
    age = models.IntegerField(editable=False, null=True)

    # Gender
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # Marital status
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)

    # Contact information
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField()
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_number = models.CharField(max_length=20)

    # Identification
    nid_number = models.CharField(max_length=50, unique=True)
    passport_number = models.CharField(max_length=50, blank=True)

    # Occupation
    occupation = models.CharField(max_length=200)
    organization_name = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Family information (for family membership)
    spouse_name = models.CharField(max_length=200, blank=True)
    number_of_children = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        default=0
    )
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)

    # File uploads - Step 1
    photo = models.ImageField(
        upload_to='photos/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='Passport-size photo (JPG/PNG, max 5MB)'
    )
    age_proof = models.FileField(
        upload_to='documents/age_proof/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Birth certificate or NID (PDF/Image, max 5MB)'
    )
    driving_license = models.FileField(
        upload_to='documents/licenses/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text='Driving license (optional, PDF/Image, max 5MB)'
    )

    # Step 2: Address Information
    present_address = models.TextField(help_text='Full present address')
    permanent_address = models.TextField(help_text='Full permanent address')

    # Step 4: Physical Measurements
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(10), MaxValueValidator(500)],
        help_text='Weight in kg'
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text='Height in cm'
    )

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
    ]
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)

    # Medical history
    surgery_history = models.TextField(
        blank=True,
        help_text='List any previous surgeries (optional)'
    )
    medical_records = models.FileField(
        upload_to='documents/medical/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text='Medical records (optional, PDF/Image, max 5MB)'
    )
    prescription = models.FileField(
        upload_to='documents/prescriptions/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text='Current prescriptions (optional, PDF/Image, max 5MB)'
    )

    # Declaration acceptance
    terms_accepted = models.BooleanField(default=False)
    declaration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Membership Application'
        verbose_name_plural = 'Membership Applications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['proposal_number']),
            models.Index(fields=['nid_number']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate proposal number if not exists
        if not self.proposal_number:
            self.proposal_number = self.generate_proposal_number()

        # Auto-calculate age from date of birth
        if self.date_of_birth:
            today = timezone.now().date()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )

        super().save(*args, **kwargs)

    def generate_proposal_number(self):
        """Generate unique proposal number: BL-YYYYMM-XXXX"""
        from datetime import datetime
        today = datetime.now()
        prefix = f"BL-{today.strftime('%Y%m')}"

        # Get last proposal number for this month
        last_application = MembershipApplication.objects.filter(
            proposal_number__startswith=prefix
        ).order_by('-proposal_number').first()

        if last_application:
            try:
                last_number = int(last_application.proposal_number.split('-')[-1])
            except Exception:
                last_number = 0
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}-{new_number:04d}"

    def __str__(self):
        return f"{self.proposal_number} - {self.first_name} {self.last_name}"


class Nominee(models.Model):
    """
    Nominee details linked to membership application
    Each application can have up to 3 nominees
    """
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='nominees'
    )

    # Nominee details
    name = models.CharField(max_length=200)

    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('other', 'Other'),
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)

    mobile_number = models.CharField(max_length=20)
    nid_number = models.CharField(max_length=50)
    date_of_birth = models.DateField()

    # Share percentage (must total 100% across all nominees)
    share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ID proof upload
    id_proof = models.FileField(
        upload_to='documents/nominee_id/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='NID or other ID proof (PDF/Image, max 5MB)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Nominee'
        verbose_name_plural = 'Nominees'

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.share_percentage}%"


class ApplicationStatusHistory(models.Model):
    """Track status changes for auditing"""
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.CharField(max_length=200, blank=True)  # Admin username
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Status History'
        verbose_name_plural = 'Status Histories'

    def __str__(self):
        return f"{self.application.proposal_number}: {self.previous_status} → {self.new_status}"
