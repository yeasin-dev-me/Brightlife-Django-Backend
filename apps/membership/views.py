from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
import logging

from .models import MembershipApplication, Nominee, MedicalRecord
from .serializers import (
    MembershipApplicationSerializer,
    MembershipApplicationListSerializer,
    MemberLoginSerializer,
    MemberProfileSerializer,
)

logger = logging.getLogger('membership')


class MemberLoginView(APIView):
    """
    Member Login API
    POST /api/v1/membership/login/
    
    Authenticates members using Proposal Number + Birth Year
    Returns member profile data on success
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate member and return profile
        
        Request Body:
        {
            "proposalNo": "BL-202512-0001",
            "birthYear": 1990
        }
        
        Response (Success):
        {
            "success": true,
            "message": "Login successful",
            "data": {
                "member": { ... member profile ... },
                "token": "..." (optional, for session)
            }
        }
        
        Response (Failure):
        {
            "success": false,
            "message": "Invalid credentials or member not found"
        }
        """
        try:
            # Validate input
            serializer = MemberLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Invalid input',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            proposal_no = serializer.validated_data['proposalNo']
            birth_year = serializer.validated_data['birthYear']
            
            logger.info(f"Member login attempt: {proposal_no}")
            
            # Find member by proposal number (check both fields)
            member = MembershipApplication.objects.filter(
                Q(proposal_no__iexact=proposal_no) | 
                Q(proposal_number__iexact=proposal_no)
            ).first()
            
            if not member:
                logger.warning(f"Login failed: Member not found - {proposal_no}")
                return Response({
                    'success': False,
                    'message': 'Invalid credentials. Member not found.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify birth year from dob or date_of_birth
            member_dob = member.dob or member.date_of_birth
            if not member_dob:
                logger.warning(f"Login failed: No DOB on record - {proposal_no}")
                return Response({
                    'success': False,
                    'message': 'Invalid credentials. Birth year mismatch.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if member_dob.year != birth_year:
                logger.warning(f"Login failed: Birth year mismatch - {proposal_no}")
                return Response({
                    'success': False,
                    'message': 'Invalid credentials. Birth year mismatch.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check membership status
            status_message = None
            if member.status == 'pending':
                status_message = 'Your application is pending review.'
            elif member.status == 'under_review':
                status_message = 'Your application is under review.'
            elif member.status == 'rejected':
                return Response({
                    'success': False,
                    'message': 'Your membership application was rejected. Please contact support.'
                }, status=status.HTTP_403_FORBIDDEN)
            elif member.status == 'expired':
                status_message = 'Your membership has expired. Please renew.'
            
            # Check validity date
            if member.valid_until and member.valid_until < timezone.now().date():
                status_message = 'Your membership has expired. Please renew.'
            
            # Serialize member profile
            profile_serializer = MemberProfileSerializer(member)
            
            logger.info(f"Member login successful: {proposal_no} - {member.name_english}")
            
            response_data = {
                'success': True,
                'message': 'Login successful',
                'data': {
                    'member': profile_serializer.data,
                    # Add status message if applicable
                    'statusMessage': status_message,
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Member login error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Server error. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MembershipApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for membership application CRUD operations
    Handles multipart/form-data with files and nested data
    """
    queryset = MembershipApplication.objects.prefetch_related('nominees', 'medical_records_files').all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return MembershipApplicationListSerializer
        return MembershipApplicationSerializer

    def get_permissions(self):
        """
        Public access for create
        Admin access for list, update, delete
        """
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Handle new membership application submission
        Processes FormData with files and nested nominee data
        """
        try:
            # Log incoming request data
            logger.info(f"Received membership application submission")
            logger.info(f"Request data keys: {list(request.data.keys())}")
            logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
            # Parse nominees from FormData array format
            nominees_data = []
            i = 0
            while True:
                name_key = f'nominees[{i}]name'
                if name_key not in request.data:
                    break
                
                relation = request.data.get(f'nominees[{i}]relation', '')
                
                # Map relation to relationship (normalize)
                relation_mapping = {
                    'son': 'child',
                    'daughter': 'child',
                    'wife': 'spouse',
                    'husband': 'spouse',
                    'father': 'father',
                    'mother': 'mother',
                    'brother': 'sibling',
                    'sister': 'sibling'
                }
                relationship = relation_mapping.get(relation.lower().strip(), 'child')
                
                nominee = {
                    'name': request.data.get(f'nominees[{i}]name', ''),
                    'relation': relation,
                    'relationship': relationship,
                    'share': int(request.data.get(f'nominees[{i}]share', 0)),
                    'age': int(request.data.get(f'nominees[{i}]age', 0)),
                }
                
                # Handle nominee photo (only add if file exists)
                photo_key = f'nominees[{i}]photo'
                if photo_key in request.FILES:
                    nominee['photo'] = request.FILES[photo_key]
                
                # Handle nominee ID proof (only add if file exists)
                id_proof_key = f'nomineeIdProof[{i}]'
                if id_proof_key in request.FILES:
                    nominee['id_proof'] = request.FILES[id_proof_key]
                
                nominees_data.append(nominee)
                i += 1
            
            logger.debug(f"Parsed {len(nominees_data)} nominees")
            
            # Prepare data for serializer - filter out empty values
            data = {}
            for key, value in request.data.items():
                # Skip nominee-related keys as they're already parsed
                if key.startswith('nominees[') or key.startswith('nomineeIdProof['):
                    continue
                # Skip empty values
                if value != '' and value is not None:
                    data[key] = value
            
            # Add parsed nominees
            if nominees_data:
                data['nominees'] = nominees_data
            
            # Handle medical records (multiple files)
            medical_records = []
            for key in request.FILES:
                if key.startswith('medicalRecords'):
                    medical_records.append(request.FILES[key])
            if medical_records:
                data['medical_records'] = medical_records
            
            # Handle age proof as JSON array
            import json
            if 'ageProof' in data:
                if isinstance(data['ageProof'], str):
                    try:
                        # Try to parse as JSON first
                        parsed = json.loads(data['ageProof'])
                        # Ensure it's a list
                        data['age_proof'] = parsed if isinstance(parsed, list) else [parsed]
                    except (json.JSONDecodeError, ValueError):
                        # If not valid JSON, treat as single string value
                        data['age_proof'] = [data['ageProof']]
                elif isinstance(data['ageProof'], list):
                    data['age_proof'] = data['ageProof']
                else:
                    data['age_proof'] = [str(data['ageProof'])]
                # Remove the old key
                data.pop('ageProof', None)
            
            # Map frontend field names to backend
            field_mapping = {
                'proposalNo': 'proposal_no',
                'foCode': 'fo_code',
                'foName': 'fo_name',
                'membershipType': 'membership_type',
                'nameBangla': 'name_bangla',
                'nameEnglish': 'name_english',
                'fatherName': 'father_name',
                'motherName': 'mother_name',
                'spouseName': 'spouse_name',
                'ageProofDoc': 'age_proof_doc',
                'drivingLicense': 'driving_license',
                'licenseDoc': 'license_doc',
                'maritalStatus': 'marital_status',
                'professionalQualifications': 'professional_qualifications',
                'organizationDetails': 'organization_details',
                'dailyWork': 'daily_work',
                'annualIncome': 'annual_income',
                'monthlyIncome': 'monthly_income',
                'incomeSource': 'income_source',
                'presentAddress': 'present_address',
                'permanentAddress': 'permanent_address',
                'bloodGroup': 'blood_group',
                'surgeryDetails': 'surgery_details',
                'acceptTerms': 'accept_terms',
            }
            
            for old_key, new_key in field_mapping.items():
                if old_key in data:
                    data[new_key] = data.pop(old_key)
            
            # Map membership_type from frontend to backend choices
            if 'membership_type' in data:
                membership_mapping = {
                    'silver': 'individual',
                    'bronze': 'individual',
                    'gold': 'family',
                    'executive': 'corporate'
                }
                data['membership_type'] = membership_mapping.get(
                    data['membership_type'].lower(), 
                    data['membership_type']
                )
            
            # Map marital_status from frontend to backend choices
            if 'marital_status' in data:
                marital_mapping = {
                    'unmarried': 'single',
                    'married': 'married',
                    'divorced': 'divorced',
                    'others': 'widowed'
                }
                data['marital_status'] = marital_mapping.get(
                    data['marital_status'].lower(),
                    data['marital_status']
                )
            
            # Convert annual income to monthly if provided
            if 'annual_income' in data:
                try:
                    annual = float(data.pop('annual_income'))
                    # Round to 2 decimal places to avoid precision issues
                    data['monthly_income'] = round(annual / 12, 2)
                except (ValueError, TypeError):
                    pass
            
            # Handle file uploads
            for file_field in ['photo', 'age_proof_doc', 'license_doc']:
                if file_field in request.FILES:
                    data[file_field] = request.FILES[file_field]
            
            # Serialize and validate
            serializer = self.get_serializer(data=data)
            
            # Add debug logging
            logger.debug(f"Serializer input data keys: {list(data.keys())}")
            if 'nominees' in data:
                logger.debug(f"Nominees data: {data['nominees']}")
            if 'age_proof' in data:
                logger.debug(f"Age proof data: {data['age_proof']}")
            
            if serializer.is_valid():
                application = serializer.save()
                
                logger.info(
                    f"New membership application submitted: {application.proposal_no} "
                    f"by {application.name_english}"
                )
                
                return Response({
                    'success': True,
                    'message': 'Membership application submitted successfully',
                    'data': {
                        'id': str(application.id),
                        'proposal_no': application.proposal_no,
                        'status': application.status,
                        'submitted_at': application.created_at.isoformat()
                    }
                }, status=status.HTTP_201_CREATED)
            
            # Log validation errors in detail
            logger.error(f"Validation errors: {serializer.errors}")
            for field, errors in serializer.errors.items():
                logger.error(f"Field '{field}': {errors}")
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error submitting membership application: {str(e)}")
            return Response({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Get application details"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Application not found',
                'errors': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        """List all applications"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
