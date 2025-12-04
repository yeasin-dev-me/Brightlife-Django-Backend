from datetime import date

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from .models import MembershipApplication


class MembershipApplicationModelTest(TestCase):
    """Test membership application model"""

    def setUp(self):
        self.application = MembershipApplication.objects.create(
            membership_type="individual",
            first_name="John",
            last_name="Doe",
            name_english="John Doe",
            date_of_birth=date(1990, 1, 1),
            dob=date(1990, 1, 1),
            gender="male",
            marital_status="single",
            mobile_number="01712345678",
            mobile="01712345678",
            email="john.doe@example.com",
            emergency_contact_name="Jane Doe",
            emergency_contact_number="01798765432",
            nid_number="1234567890",
            occupation="service",
            father_name="Father Name",
            mother_name="Mother Name",
            present_address="123 Main St",
            permanent_address="123 Main St",
            weight="70.5",
            height="5'9\"",
            blood_group="O+",
            terms_accepted=True,
            accept_terms=True,
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
        data = {
            "membershipType": "individual",
            "nameEnglish": "Test User",
            "fatherName": "Father",
            "motherName": "Mother",
            "dob": "1995-05-15",
            "gender": "male",
            "maritalStatus": "unmarried",
            "mobile": "01712345678",
            "email": "test@example.com",
            "presentAddress": "Present Address",
            "permanentAddress": "Permanent Address",
            "occupation": "service",
            "bloodGroup": "A+",
            "weight": "75",
            "height": "5'10\"",
            "acceptTerms": "true",
            "nominees[0]name": "Nominee 1",
            "nominees[0]relation": "wife",
            "nominees[0]share": "100",
            "nominees[0]age": "28",
        }

        response = self.client.post(
            "/api/v1/membership/applications/", data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("proposal_no", response.data["data"])

    def test_invalid_share_percentage(self):
        """Test validation of nominee share percentages"""
        # Test data with shares not totaling 100%
        data = {
            "membershipType": "individual",
            "nameEnglish": "Test User",
            "fatherName": "Father",
            "motherName": "Mother",
            "dob": "1995-05-15",
            "gender": "male",
            "maritalStatus": "unmarried",
            "mobile": "01712345679",
            "email": "test2@example.com",
            "presentAddress": "Present Address",
            "permanentAddress": "Permanent Address",
            "occupation": "business",
            "bloodGroup": "A+",
            "weight": "75",
            "height": "5'10\"",
            "acceptTerms": "true",
            "nominees[0]name": "Nominee 1",
            "nominees[0]relation": "wife",
            "nominees[0]share": "50",
            "nominees[0]age": "28",
        }

        response = self.client.post(
            "/api/v1/membership/applications/", data, format="multipart"
        )
        # Expect validation error because total share != 100
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
