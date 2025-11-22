from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import PaymentProof


class PaymentProofModelTest(TestCase):
    """Test PaymentProof model"""
    
    def setUp(self):
        self.payment = PaymentProof.objects.create(
            transaction_id='TEST123',
            payment_method='bkash',
            amount=Decimal('1000.00'),
            payer_name='Test User',
            payer_contact='01712345678'
        )
    
    def test_payment_creation(self):
        """Test payment proof creation"""
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(str(self.payment), 'TEST123 - Test User (pending)')
    
    def test_verify_payment(self):
        """Test payment verification"""
        self.payment.verify()
        self.assertEqual(self.payment.status, 'verified')
        self.assertIsNotNone(self.payment.verified_at)
    
    def test_reject_payment(self):
        """Test payment rejection"""
        self.payment.reject('Invalid transaction')
        self.assertEqual(self.payment.status, 'rejected')
        self.assertEqual(self.payment.rejection_reason, 'Invalid transaction')


class PaymentProofAPITest(APITestCase):
    """Test Payment Proof API endpoints"""
    
    def test_submit_payment_proof(self):
        """Test submitting payment proof"""
        data = {
            'transaction_id': 'TEST456',
            'payment_method': 'bkash',
            'amount': '2000.00',
            'payer_name': 'API Test User',
            'payer_contact': '01812345678',
            'notes': 'Test payment'
        }
        
        response = self.client.post('/api/v1/payment/proof/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('transactionId', response.data['data'])
    
    def test_submit_invalid_payment(self):
        """Test submitting invalid payment proof"""
        data = {
            'transaction_id': 'TEST789',
            'payment_method': 'invalid',
            'amount': '-100',
            'payer_name': '',
            'payer_contact': 'invalid'
        }
        
        response = self.client.post('/api/v1/payment/proof/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_payment_status(self):
        """Test retrieving payment status"""
        # Create a payment first
        payment = PaymentProof.objects.create(
            transaction_id='STATUS123',
            payment_method='bank-transfer',
            amount=Decimal('5000.00'),
            payer_name='Status Test',
            payer_contact='01912345678'
        )
        
        response = self.client.get(f'/api/v1/payment/proof/{payment.transaction_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['status'], 'pending')
    
    def test_get_nonexistent_payment(self):
        """Test retrieving non-existent payment"""
        response = self.client.get('/api/v1/payment/proof/NONEXISTENT/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
