import logging

from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response

from .models import AgentApplication
from .serializers import (
	AgentApplicationListSerializer,
	AgentApplicationSerializer,
)

logger = logging.getLogger("agents")


class AgentApplicationViewSet(viewsets.ModelViewSet):
	"""Handles CRUD actions for agent applications."""

	queryset = AgentApplication.objects.all()
	parser_classes = [MultiPartParser, FormParser]
	throttle_classes = [ScopedRateThrottle]
	throttle_scope = "agent-onboarding"

	def get_permissions(self):
		if self.action == "create":
			return [permissions.AllowAny()]
		return [permissions.IsAdminUser()]

	def get_serializer_class(self):
		if self.action == "list":
			return AgentApplicationListSerializer
		return AgentApplicationSerializer

	def create(self, request, *args, **kwargs):
		payload = self._transform_request_data(request)
		serializer = self.get_serializer(data=payload)

		if serializer.is_valid():
			application = serializer.save(
				user_agent=request.META.get("HTTP_USER_AGENT", ""),
				ip_address=self._get_client_ip(request),
			)
			logger.info("Agent application submitted: %s", application.agent_id)

			return Response(
				{
					"success": True,
					"message": "Agent registration submitted successfully",
					"data": {
						"id": str(application.id),
						"agentId": application.agent_id,
						"status": application.status,
						"submittedAt": application.submitted_at.isoformat(),
					},
				},
				status=status.HTTP_201_CREATED,
			)

		logger.warning("Agent application validation failed: %s", serializer.errors)
		return Response(
			{
				"success": False,
				"message": "Registration failed. Please fix the highlighted fields.",
				"errors": serializer.errors,
			},
			status=status.HTTP_400_BAD_REQUEST,
		)

	def _transform_request_data(self, request):
		data = {}
		field_mapping = {
			"applicantRole": "applicant_role",
			"agentId": "agent_id",
			"fmName": "fm_name",
			"roleCode": "role_code",
			"dgmName": "dgm_name",
			"dgmCode": "dgm_code",
			"gmName": "gm_name",
			"gmCode": "gm_code",
			"fullName": "full_name",
			"email": "email",
			"phone": "phone",
			"address": "address",
			"guardianName": "guardian_name",
			"motherName": "mother_name",
			"presentAddress": "present_address",
			"permanentAddress": "permanent_address",
			"dob": "dob",
			"birthPlace": "birth_place",
			"nidNumber": "nid_number",
			"bankAccountNumber": "bank_account_number",
			"bankName": "bank_name",
			"bankBranchName": "bank_branch_name",
		}

		for source_key, target_key in field_mapping.items():
			value = request.data.get(source_key)
			if value not in [None, ""]:
				data[target_key] = value

		file_mapping = {
			"applicantPhoto": "applicant_photo",
			"nidDocument": "nid_document",
			"educationCertificate": "education_certificate",
		}

		for source_key, target_key in file_mapping.items():
			if file := request.FILES.get(source_key):
				data[target_key] = file

		data["password"] = request.data.get("password", "")
		data["confirm_password"] = request.data.get("confirmPassword", "")

		agree_terms_raw = str(request.data.get("agreeTerms", "false")).lower()
		data["agree_terms"] = agree_terms_raw in {"true", "1", "yes", "on"}

		# Normalize phone number to avoid formatting issues
		if phone := data.get("phone"):
			data["phone"] = phone.replace(" ", "").strip()

		return data

	def _get_client_ip(self, request):
		forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
		if forwarded_for:
			return forwarded_for.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR")
