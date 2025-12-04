from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MembershipApplication, Nominee


class MembershipApplicationModelTest(TestCase):
    """Test membership application model"""

    def setUp(self):
        self.photo = SimpleUploadedFile(
            "photo.jpg", b"file_content", content_type="image/jpeg"
        )
        self.age_proof = SimpleUploadedFile(
            "age_proof.pdf", b"file_content", content_type="application/pdf"
        )

        self.application = MembershipApplication.objects.create(
            membership_type="individual",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            marital_status="single",
            mobile_number="01712345678",
            email="john.doe@example.com",
            emergency_contact_name="Jane Doe",
            emergency_contact_number="01798765432",
            nid_number="1234567890",
            occupation="Engineer",
            father_name="Father Name",
            mother_name="Mother Name",
            present_address="123 Main St",
            permanent_address="123 Main St",
            weight=Decimal("70.5"),
            height=Decimal("175.0"),
            blood_group="O+",
            terms_accepted=True,
            photo=self.photo,
            age_proof=self.age_proof,
        )

    def test_proposal_number_generation(self):
        """Test auto-generation of proposal number"""
        self.assertTrue(self.application.proposal_number.startswith("BL-"))

    def test_age_calculation(self):
        """Test automatic age calculation"""
        expected_age = 35  # As of 2025
        self.assertEqual(self.application.age, expected_age)

    def test_string_representation(self):
        """Test __str__ method"""
        expected = f"{self.application.proposal_number} - John Doe"
        self.assertEqual(str(self.application), expected)


class MembershipAPITest(APITestCase):
    """Test membership API endpoints"""

    def test_create_application(self):
        """Test creating new membership application"""
        photo = SimpleUploadedFile(
            "photo.jpg", b"file_content", content_type="image/jpeg"
        )
        age_proof = SimpleUploadedFile(
            "age_proof.pdf", b"file_content", content_type="application/pdf"
        )
        nominee_id = SimpleUploadedFile(
            "nominee_id.pdf", b"file_content", content_type="application/pdf"
        )

        data = {
            "membership_type": "individual",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1995-05-15",
            "gender": "male",
            "marital_status": "single",
            "mobile_number": "01712345678",
            "email": "test@example.com",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_number": "01798765432",
            "nid_number": "9876543210",
            "occupation": "Developer",
            "father_name": "Father",
            "mother_name": "Mother",
            "present_address": "Present Address",
            "permanent_address": "Permanent Address",
            "weight": "75.0",
            "height": "180.0",
            "blood_group": "A+",
            "terms_accepted": True,
            "photo": photo,
            "age_proof": age_proof,
            "nominees": [
                {
                    "name": "Nominee 1",
                    "relationship": "spouse",
                    "mobile_number": "01712345679",
                    "nid_number": "1111111111",
                    "date_of_birth": "1996-06-20",
                    "share_percentage": "100",
                    "id_proof": nominee_id,
                }
            ],
        }

        response = self.client.post(
            "/api/v1/membership/applications/", data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("proposal_number", response.data["data"])

    def test_invalid_share_percentage(self):
        """Test validation of nominee share percentages"""
        # Test data with shares not totaling 100%
        photo = SimpleUploadedFile(
            "photo.jpg", b"file_content", content_type="image/jpeg"
        )
        age_proof = SimpleUploadedFile(
            "age_proof.pdf", b"file_content", content_type="application/pdf"
        )
        nominee_id = SimpleUploadedFile(
            "nominee_id.pdf", b"file_content", content_type="application/pdf"
        )

        data = {
            "membership_type": "individual",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1995-05-15",
            "gender": "male",
            "marital_status": "single",
            "mobile_number": "01712345678",
            "email": "test2@example.com",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_number": "01798765432",
            "nid_number": "9876543211",
            "occupation": "Developer",
            "father_name": "Father",
            "mother_name": "Mother",
            "present_address": "Present Address",
            "permanent_address": "Permanent Address",
            "weight": "75.0",
            "height": "180.0",
            "blood_group": "A+",
            "terms_accepted": True,
            "photo": photo,
            "age_proof": age_proof,
            "nominees": [
                {
                    "name": "Nominee 1",
                    "relationship": "spouse",
                    "mobile_number": "01712345679",
                    "nid_number": "1111111112",
                    "date_of_birth": "1996-06-20",
                    "share_percentage": "50",
                    "id_proof": nominee_id,
                }
            ],
        }

        response = self.client.post(
            "/api/v1/membership/applications/", data, format="multipart"
        )
        # Expect validation error because total share != 100
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
