import uuid

from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models


class AgentApplication(models.Model):
    """Represents a submitted agent onboarding form."""

    ROLE_CHOICES = [
        ("FO", "Field Officer"),
        ("FM", "Field Manager"),
        ("DGM", "Deputy General Manager"),
        ("GM", "General Manager"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    PHONE_VALIDATOR = RegexValidator(
        regex=r"^[0-9+\-()\s]{8,20}$",
        message="Provide a valid phone number",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=50, unique=True)
    applicant_role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    fm_name = models.CharField(max_length=200)
    role_code = models.CharField(max_length=50)
    dgm_name = models.CharField(max_length=200)
    dgm_code = models.CharField(max_length=50)
    gm_name = models.CharField(max_length=200)
    gm_code = models.CharField(max_length=50)

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, validators=[PHONE_VALIDATOR])

    address = models.TextField()
    guardian_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    present_address = models.TextField()
    permanent_address = models.TextField()

    dob = models.DateField()
    birth_place = models.CharField(max_length=120)
    nid_number = models.CharField(max_length=40)

    bank_account_number = models.CharField(max_length=60)
    bank_name = models.CharField(max_length=120)
    bank_branch_name = models.CharField(max_length=120)

    applicant_photo = models.ImageField(
        upload_to="agents/photos/%Y/%m/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"])],
    )
    nid_document = models.FileField(
        upload_to="agents/nid/%Y/%m/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "pdf"])],
    )
    education_certificate = models.FileField(
        upload_to="agents/education/%Y/%m/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "pdf"])],
    )

    password_hash = models.CharField(max_length=128)
    agree_terms = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.CharField(max_length=150, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Agent Application"
        verbose_name_plural = "Agent Applications"
        indexes = [
            models.Index(fields=["agent_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-submitted_at"]),
        ]

    def __str__(self):
        return f"{self.agent_id} - {self.full_name}"
