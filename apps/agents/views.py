import json
import logging
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from .models import AgentApplication
from .serializers import (
	AgentApplicationListSerializer,
	AgentApplicationSerializer,
)

logger = logging.getLogger("agents")


class AgentOnboardingThrottleBase(SimpleRateThrottle):
	"""Common throttle base that keys on client IP and logs abuse."""

	scope = "agent-onboarding"

	def __init__(self):
		super().__init__()
		self._ident = None

	def get_ident(self, request):
		forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
		if forwarded_for:
			return forwarded_for.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR")

	def get_cache_key(self, request, view):
		if request.method.upper() != "POST":
			return None
		ident = self.get_ident(request)
		if not ident:
			return None
		self._ident = ident
		return self.cache_format % {"scope": self.scope, "ident": ident}

	def allow_request(self, request, view):
		allowed = super().allow_request(request, view)
		if not allowed:
			logger.warning(
				"Agent onboarding throttle '%s' triggered for IP %s",
				self.scope,
				self._ident or self.get_ident(request) or "unknown",
			)
		return allowed


class AgentOnboardingBurstThrottle(AgentOnboardingThrottleBase):
	scope = "agent-onboarding-burst"


class AgentOnboardingHourlyThrottle(AgentOnboardingThrottleBase):
	scope = "agent-onboarding"


class AgentApplicationViewSet(viewsets.ModelViewSet):
	"""Handles CRUD actions for agent applications."""

	queryset = AgentApplication.objects.all()
	parser_classes = [MultiPartParser, FormParser]
	throttle_classes = [AgentOnboardingBurstThrottle, AgentOnboardingHourlyThrottle]

	def get_permissions(self):
		if self.action == "create":
			return [permissions.AllowAny()]
		return [permissions.IsAdminUser()]

	def get_serializer_class(self):
		if self.action == "list":
			return AgentApplicationListSerializer
		return AgentApplicationSerializer

	def create(self, request, *args, **kwargs):
		if captcha_error := self._enforce_captcha(request):
			logger.warning(
				"Agent onboarding captcha rejected for IP %s: %s",
				self._get_client_ip(request),
				captcha_error,
			)
			return Response(
				{
					"success": False,
					"message": captcha_error,
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

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

	def _enforce_captcha(self, request):
		provider = settings.AGENT_ONBOARDING_CAPTCHA_PROVIDER
		secret = settings.AGENT_ONBOARDING_CAPTCHA_SECRET
		if not provider or not secret:
			return None

		token = request.data.get("captchaToken") or request.data.get("cfTurnstileResponse")
		if not token:
			return "Captcha verification is required. Please refresh and try again."

		remote_ip = self._get_client_ip(request)
		success, error_message = self._verify_captcha(provider, secret, token, remote_ip)
		if success:
			return None
		return error_message or "Captcha verification failed."

	def _verify_captcha(self, provider, secret, token, remote_ip):
		payload = {
			"secret": secret,
			"response": token,
		}
		if remote_ip:
			payload["remoteip"] = remote_ip

		if provider == "recaptcha":
			endpoint = "https://www.google.com/recaptcha/api/siteverify"
		elif provider == "turnstile":
			endpoint = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
		else:
			logger.error("Unsupported CAPTCHA provider configured: %s", provider)
			return False, "Captcha configuration error. Please contact support."

		try:
			encoded = urllib_parse.urlencode(payload).encode()
			req = urllib_request.Request(
				endpoint,
				data=encoded,
				method="POST",
				headers={"Content-Type": "application/x-www-form-urlencoded"},
			)
			with urllib_request.urlopen(req, timeout=5) as response:
				result = json.loads(response.read().decode("utf-8"))
		except Exception as exc:  # pragma: no cover - network error
			logger.error("Captcha verification error: %s", exc, exc_info=True)
			return False, "Captcha verification is temporarily unavailable. Please retry."

		if provider == "recaptcha":
			score = result.get("score", 0)
			if result.get("success") and score >= settings.AGENT_ONBOARDING_CAPTCHA_SCORE_THRESHOLD:
				return True, None
			logger.warning(
				"reCAPTCHA rejected submission (score=%s, errors=%s)",
				score,
				result.get("error-codes"),
			)
			return False, "Captcha verification failed. Please try again."

		if provider == "turnstile":
			if result.get("success"):
				return True, None
			logger.warning(
				"Cloudflare Turnstile rejected submission (errors=%s)",
				result.get("error-codes"),
			)
			return False, "Captcha verification failed. Please try again."

		return False, "Captcha verification failed."
