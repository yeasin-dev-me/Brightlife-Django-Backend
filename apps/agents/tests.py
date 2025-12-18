from io import BytesIO

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image


def build_test_png():
    buffer = BytesIO()
    image = Image.new("RGB", (2, 2), color="blue")
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile("photo.png", buffer.read(), content_type="image/png")


class AgentApplicationAPITests(APITestCase):
    def test_can_submit_agent_application(self):
        url = reverse("agents:agent-application-list")
        payload = {
            "applicantRole": "FO",
            "agentId": "AG-1001",
            "fmName": "Field Manager",
            "roleCode": "FO-001",
            "dgmName": "Deputy GM",
            "dgmCode": "DGM-01",
            "gmName": "General Manager",
            "gmCode": "GM-01",
            "fullName": "Jane Agent",
            "email": "agent@example.com",
            "phone": "+880123456789",
            "address": "Corporate HQ",
            "guardianName": "Guardian Name",
            "motherName": "Mother Name",
            "presentAddress": "Present address",
            "permanentAddress": "Permanent address",
            "dob": "1990-01-01",
            "birthPlace": "Dhaka",
            "nidNumber": "1234567890",
            "bankAccountNumber": "987654321",
            "bankName": "Bank of Test",
            "bankBranchName": "Dhaka Branch",
            "password": "Str0ngPass!",
            "confirmPassword": "Str0ngPass!",
            "agreeTerms": "true",
            "applicantPhoto": build_test_png(),
            "nidDocument": SimpleUploadedFile(
                "nid.pdf", b"filecontent", content_type="application/pdf"
            ),
            "educationCertificate": build_test_png(),
        }

        response = self.client.post(url, data=payload, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("success"))
