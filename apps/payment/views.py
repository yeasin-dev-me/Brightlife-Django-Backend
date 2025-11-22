from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Q
import logging

from .models import PaymentProof
from .serializers import (
    PaymentProofSerializer,
    PaymentProofListSerializer,
    PaymentProofAdminSerializer
)

logger = logging.getLogger('payment')


class PaymentProofSubmitView(APIView):
    """API view for submitting payment proof"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @transaction.atomic
    def post(self, request):
        """Handle payment proof submission"""
        try:
            logger.info(f"Received payment proof submission")
            logger.debug(f"Request data keys: {list(request.data.keys())}")
            logger.debug(f"Request FILES keys: {list(request.FILES.keys())}")
            
            # Create serializer with request data
            serializer = PaymentProofSerializer(data=request.data)
            
            if serializer.is_valid():
                # Save with additional metadata
                payment_proof = serializer.save(
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                logger.info(
                    f"Payment proof submitted: {payment_proof.transaction_id} "
                    f"by {payment_proof.payer_name} - Amount: {payment_proof.amount}"
                )
                
                # TODO: Send notification email to admin
                # TODO: Send confirmation email to payer
                
                # Generate money receipt data for frontend
                receipt_data = {
                    'receiptNumber': payment_proof.transaction_id,
                    'receiptDate': payment_proof.submitted_at.strftime('%B %d, %Y'),
                    'receiptTime': payment_proof.submitted_at.strftime('%I:%M %p'),
                    'payerName': payment_proof.payer_name,
                    'payerContact': payment_proof.payer_contact,
                    'amount': str(payment_proof.amount),
                    'paymentMethod': payment_proof.get_payment_method_display(),
                    'transactionId': payment_proof.transaction_id,
                    'status': payment_proof.get_status_display(),
                    'submittedAt': payment_proof.submitted_at.isoformat(),
                    'notes': payment_proof.notes or '',
                    'membershipApplicationId': payment_proof.membership_application.application_id if payment_proof.membership_application else None,
                    # Company/Organization details
                    'organization': {
                        'name': 'Brightlife Bangladesh',
                        'address': 'Dhaka, Bangladesh',
                        'phone': '+880-XXX-XXXXXX',
                        'email': 'info@brightlife-bd.com',
                        'website': 'www.brightlife-bd.com'
                    },
                    'verificationMessage': 'This is a computer-generated receipt for payment proof submission. Your payment will be verified within 24-48 hours. Please keep this receipt for your records.'
                }
                
                return Response({
                    'success': True,
                    'message': 'Payment proof submitted successfully. We will verify your payment within 24-48 hours.',
                    'data': {
                        'id': str(payment_proof.id),
                        'transactionId': payment_proof.transaction_id,
                        'status': payment_proof.status,
                        'submittedAt': payment_proof.submitted_at.isoformat(),
                        'receipt': receipt_data
                    }
                }, status=status.HTTP_201_CREATED)
            
            # Log validation errors
            logger.error(f"Payment proof validation errors: {serializer.errors}")
            for field, errors in serializer.errors.items():
                logger.error(f"Field '{field}': {errors}")
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error submitting payment proof: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'An error occurred while processing your request: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentProofStatusView(APIView):
    """API view for checking payment proof status"""
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get(self, request, transaction_id):
        """Get payment proof status by transaction ID"""
        try:
            payment_proof = PaymentProof.objects.get(
                transaction_id=transaction_id
            )
            
            return Response({
                'success': True,
                'message': 'Payment proof found',
                'data': {
                    'id': str(payment_proof.id),
                    'transactionId': payment_proof.transaction_id,
                    'paymentMethod': payment_proof.payment_method,
                    'amount': str(payment_proof.amount),
                    'payerName': payment_proof.payer_name,
                    'status': payment_proof.status,
                    'submittedAt': payment_proof.submitted_at.isoformat(),
                    'verifiedAt': payment_proof.verified_at.isoformat() if payment_proof.verified_at else None,
                    'rejectionReason': payment_proof.rejection_reason if payment_proof.status == 'rejected' else None
                }
            }, status=status.HTTP_200_OK)
        
        except PaymentProof.DoesNotExist:
            logger.warning(f"Payment proof not found: {transaction_id}")
            return Response({
                'success': False,
                'message': 'Payment proof not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error retrieving payment proof: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'An error occurred while retrieving payment proof'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentProofViewSet(viewsets.ModelViewSet):
    """ViewSet for admin management of payment proofs"""
    queryset = PaymentProof.objects.all()
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return PaymentProofListSerializer
        return PaymentProofAdminSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PaymentProof.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment method
        method_filter = self.request.query_params.get('payment_method', None)
        if method_filter:
            queryset = queryset.filter(payment_method=method_filter)
        
        # Search by transaction ID or payer name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search) |
                Q(payer_name__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a payment proof"""
        payment_proof = self.get_object()
        
        if payment_proof.status == 'verified':
            return Response({
                'success': False,
                'message': 'Payment proof is already verified'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_proof.verify(user=request.user)
        
        # TODO: Send verification email to payer
        
        return Response({
            'success': True,
            'message': 'Payment proof verified successfully',
            'data': PaymentProofAdminSerializer(payment_proof).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a payment proof"""
        payment_proof = self.get_object()
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response({
                'success': False,
                'message': 'Rejection reason is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment_proof.status == 'rejected':
            return Response({
                'success': False,
                'message': 'Payment proof is already rejected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_proof.reject(reason=reason, user=request.user)
        
        # TODO: Send rejection email to payer
        
        return Response({
            'success': True,
            'message': 'Payment proof rejected',
            'data': PaymentProofAdminSerializer(payment_proof).data
        })
    
    def list(self, request, *args, **kwargs):
        """List all payment proofs with custom response format"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': queryset.count()
        })
