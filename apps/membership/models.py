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
        ('active', 'Active'),
        ('rejected', 'Rejected'),
        ('under_review', 'Under Review'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Membership validity (for approved members)
    valid_until = models.DateField(null=True, blank=True, help_text='Membership validity date')

    # Step 1: Personal Information
    MEMBERSHIP_TYPE_CHOICES = [
        ('individual', 'Individual Membership'),
        ('family', 'Family Membership'),
        ('corporate', 'Corporate Membership'),
    ]
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPE_CHOICES)

    # Name fields (matching frontend)
    name_bangla = models.CharField(max_length=200, blank=True)
    name_english = models.CharField(max_length=200, blank=True, default='')
    father_name = models.CharField(max_length=200, blank=True, default='')
    mother_name = models.CharField(max_length=200, blank=True, default='')
    spouse_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Legacy fields (keeping for backwards compatibility)
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Date of birth and calculated age
    dob = models.DateField(null=True, blank=True, help_text='Date of birth')
    date_of_birth = models.DateField(null=True, blank=True, help_text='Legacy field')
    age = models.IntegerField(editable=False, null=True, blank=True)

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
    mobile = models.CharField(max_length=20, blank=True, default='', help_text='Format: +880XXXXXXXXXX')
    mobile_number = models.CharField(max_length=20, blank=True, help_text='Legacy field')
    email = models.EmailField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)

    # Nationality and age proof
    nationality = models.CharField(max_length=100, default='Bangladeshi')
    age_proof = models.JSONField(default=list, help_text='Array of selected proof types')
    age_proof_doc = models.FileField(
        upload_to='documents/age_proof/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Age proof document (PDF/Image, max 5MB)',
        blank=True,
        null=True
    )
    
    # Driving License
    DRIVING_LICENSE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    driving_license = models.CharField(max_length=3, choices=DRIVING_LICENSE_CHOICES, default='no')
    license_doc = models.FileField(
        upload_to='documents/licenses/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text='Driving license document (optional, PDF/Image, max 5MB)'
    )

    # Identification
    nid_number = models.CharField(max_length=50, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)

    # Occupation and Education
    education = models.CharField(max_length=200, blank=True)
    professional_qualifications = models.CharField(max_length=200, blank=True)
    
    OCCUPATION_CHOICES = [
        ('service', 'Service'),
        ('business', 'Business'),
        ('farmer', 'Farmer'),
        ('others', 'Others'),
    ]
    occupation = models.CharField(max_length=200, choices=OCCUPATION_CHOICES, blank=True)
    organization_name = models.CharField(max_length=200, blank=True)
    organization_details = models.TextField(blank=True)
    daily_work = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(max_length=200, blank=True)

    # Family information (for family membership)
    number_of_children = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        default=0,
        blank=True
    )

    # File uploads - Photo
    photo = models.ImageField(
        upload_to='photos/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='Passport-size photo (JPG/PNG, max 2MB)',
        blank=True,
        null=True
    )

    # Step 2: Address Information
    present_address = models.TextField(blank=True, default='', help_text='Full present address')
    permanent_address = models.TextField(blank=True, default='', help_text='Full permanent address')

    # Step 4: Physical Measurements
    weight = models.CharField(max_length=20, blank=True, help_text='Weight in kg (e.g., "70.5")')
    height = models.CharField(max_length=20, blank=True, help_text='Height in feet (e.g., "5\'8\"")')
    chest = models.CharField(max_length=20, blank=True, help_text='Chest in inches')

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
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, default='')

    # Medical history
    surgery_details = models.TextField(
        blank=True,
        help_text='List any previous surgeries (optional)'
    )

    # Declaration acceptance (matching frontend acceptTerms)
    accept_terms = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False, help_text='Legacy field')
    declaration_date = models.DateTimeField(auto_now_add=True)
    
    # Proposal Information (matching frontend)
    proposal_no = models.CharField(max_length=100, unique=True, editable=False, blank=True, default='')
    fo_code = models.CharField(max_length=50, blank=True, null=True, help_text='Field Officer Code')
    fo_name = models.CharField(max_length=200, blank=True, null=True, help_text='Field Officer Name')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Membership Application'
        verbose_name_plural = 'Membership Applications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['proposal_number']),
            models.Index(fields=['proposal_no']),
            models.Index(fields=['nid_number']),
            models.Index(fields=['dob']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate proposal number if not exists (use both fields)
        if not self.proposal_number and not self.proposal_no:
            self.proposal_number = self.generate_proposal_number()
            self.proposal_no = self.proposal_number

        # Auto-calculate age from dob or date_of_birth
        dob = self.dob or self.date_of_birth
        if dob:
            today = timezone.now().date()
            self.age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            
        # Sync legacy fields
        if self.name_english and not self.first_name:
            parts = self.name_english.split()
            self.first_name = parts[0] if parts else ''
            self.last_name = parts[-1] if len(parts) > 1 else ''
            
        if self.mobile and not self.mobile_number:
            self.mobile_number = self.mobile
            
        if self.accept_terms and not self.terms_accepted:
            self.terms_accepted = self.accept_terms

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
    Matching frontend structure
    """
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='nominees'
    )

    # Nominee details
    name = models.CharField(max_length=200)

    RELATIONSHIP_CHOICES = [
        ('child', 'Child'),        # Maps from: son, daughter
        ('spouse', 'Spouse'),      # Maps from: wife, husband
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('sibling', 'Sibling'),    # Maps from: brother, sister
    ]
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default='child')
    relation = models.CharField(max_length=50, blank=True, help_text='Original relation from frontend')

    # Share percentage (must total 100% across all nominees)
    share = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage share'
    )
    share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
        help_text='Legacy field'
    )
    
    age = models.IntegerField(default=0)
    
    # Files
    photo = models.ImageField(
        upload_to='nominee_photos/%Y/%m/',
        blank=True,
        null=True,
        help_text='Nominee photo'
    )
    id_proof = models.FileField(
        upload_to='nominee_id/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text='NID or other ID proof (PDF/Image, max 5MB)'
    )
    
    # Legacy fields
    mobile_number = models.CharField(max_length=20, blank=True)
    nid_number = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Nominee'
        verbose_name_plural = 'Nominees'
        
    def save(self, *args, **kwargs):
        # Sync share and share_percentage
        if self.share and not self.share_percentage:
            self.share_percentage = self.share
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.share}%"


class MedicalRecord(models.Model):
    """
    Medical records linked to membership application
    Supports multiple files
    """
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='medical_records_files'
    )
    file = models.FileField(
        upload_to='medical_records/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text='Medical record file (PDF/Image, max 5MB)'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medical_records'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Medical Record for {self.application.proposal_no}"


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
