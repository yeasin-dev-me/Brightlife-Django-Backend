import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from .models import ApplicationStatusHistory, MembershipApplication
from .serializers import (
    MembershipApplicationListSerializer,
    MembershipApplicationSerializer,
)

logger = logging.getLogger("membership")


class MembershipApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for membership application CRUD operations
    """

    queryset = MembershipApplication.objects.prefetch_related("nominees").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == "list":
            return MembershipApplicationListSerializer
        return MembershipApplicationSerializer

    def get_permissions(self):
        """
        Public access for create and retrieve
        Admin access for list, update, delete
        """
        if self.action in ["create", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Handle new membership application submission
        Wraps creation in database transaction for data integrity
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Save application and nominees
            application = serializer.save()

            # Log successful submission
            logger.info(
                f"New membership application submitted: {application.proposal_number} "
                f"by {application.first_name} {application.last_name}"
            )

            # Send confirmation email (optional)
            self.send_confirmation_email(application)

            # Return response with proposal number
            return Response(
                {
                    "success": True,
                    "message": "Application submitted successfully",
                    "data": {
                        "proposal_number": application.proposal_number,
                        "id": str(application.id),
                        "status": application.status,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error submitting membership application: {str(e)}")
            return Response(
                {
                    "success": False,
                    "message": "Failed to submit application",
                    "errors": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        """Get application details by ID or proposal number"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({"success": True, "data": serializer.data})
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Application not found",
                    "errors": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser]
    )
    def update_status(self, request, pk=None):
        """
        Admin endpoint to update application status
        POST /api/membership/applications/{id}/update_status/
        Body: { "status": "approved", "notes": "Optional notes" }
        """
        application = self.get_object()
        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if new_status not in dict(MembershipApplication.STATUS_CHOICES):
            return Response(
                {"success": False, "message": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Record status change in history
        ApplicationStatusHistory.objects.create(
            application=application,
            previous_status=application.status,
            new_status=new_status,
            changed_by=(
                request.user.username if request.user.is_authenticated else "system"
            ),
            notes=notes,
        )

        # Update status
        application.status = new_status
        application.save()

        # Send notification email
        self.send_status_update_email(application, new_status)

        logger.info(
            f"Application {application.proposal_number} status updated to {new_status}"
        )

        return Response(
            {
                "success": True,
                "message": "Status updated successfully",
                "data": {
                    "proposal_number": application.proposal_number,
                    "status": application.status,
                },
            }
        )

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAdminUser])
    def statistics(self, request):
        """
        Admin endpoint for application statistics
        GET /api/membership/applications/statistics/
        """
        from django.db import models as dj_models
        from django.db.models import Count

        stats = MembershipApplication.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=dj_models.Q(status="pending")),
            approved=Count("id", filter=dj_models.Q(status="approved")),
            rejected=Count("id", filter=dj_models.Q(status="rejected")),
            under_review=Count("id", filter=dj_models.Q(status="under_review")),
        )

        # Membership type breakdown
        type_breakdown = MembershipApplication.objects.values(
            "membership_type"
        ).annotate(count=Count("id"))

        return Response(
            {
                "success": True,
                "data": {"overview": stats, "by_type": list(type_breakdown)},
            }
        )

    def send_confirmation_email(self, application):
        """Send confirmation email to applicant"""
        try:
            subject = f"Membership Application Received - {application.proposal_number}"
            message = f"""
Dear {application.first_name} {application.last_name},

Thank you for submitting your membership application to BrightLife Bangladesh.

Your application details:
- Proposal Number: {application.proposal_number}
- Membership Type: {application.get_membership_type_display()}
- Submission Date: {application.created_at.strftime('%d %B %Y, %I:%M %p')}

Your application is currently under review. We will notify you once the review is complete.

For any queries, please contact us at support@brightlife-bd.com

Best regards,
BrightLife Bangladesh Team
            """

            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@brightlife-bd.com"),
                [application.email],
                fail_silently=True,
            )
            logger.info(f"Confirmation email sent to {application.email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")

    def send_status_update_email(self, application, new_status):
        """Send email when application status changes"""
        try:
            status_messages = {
                "approved": "We are pleased to inform you that your membership application has been approved!",
                "rejected": "We regret to inform you that your membership application has been rejected.",
                "under_review": "Your membership application is currently under review.",
            }

            subject = f"Application Status Update - {application.proposal_number}"
            message = f"""
Dear {application.first_name} {application.last_name},

{status_messages.get(new_status, 'Your application status has been updated.')}

Application Details:
- Proposal Number: {application.proposal_number}
- Current Status: {application.get_status_display()}

For any queries, please contact us at support@brightlife-bd.com

Best regards,
BrightLife Bangladesh Team
            """

            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@brightlife-bd.com"),
                [application.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send status update email: {str(e)}")
