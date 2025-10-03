"""
OTP verification views for email verification
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging

from .firebase_service import firebase_service

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Send OTP to user's email for verification
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                'success': False,
                'message': 'Invalid email format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP
        otp = firebase_service.generate_otp()
        
        # Store OTP
        if not firebase_service.store_otp(email, otp):
            return Response({
                'success': False,
                'message': 'Failed to generate OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Send OTP via email
        if not firebase_service.send_otp_email(email, otp):
            return Response({
                'success': False,
                'message': 'Failed to send OTP email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'message': 'OTP sent successfully to your email'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in send_otp: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code for email verification
    
    Expected payload:
    {
        "email": "user@example.com",
        "otp": "123456"
    }
    """
    try:
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({
                'success': False,
                'message': 'Email and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                'success': False,
                'message': 'Invalid email format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        result = firebase_service.verify_otp(email, otp)
        
        if not result['success']:
            return Response({
                'success': False,
                'message': result['message'],
                'error': result.get('error')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark user email as verified
        try:
            user = User.objects.get(email=email)
            user.is_verified = True
            user.save()
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in verify_otp: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP to user's email
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response({
                'success': False,
                'message': 'Invalid email format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new OTP
        otp = firebase_service.generate_otp()
        
        # Store new OTP
        if not firebase_service.store_otp(email, otp):
            return Response({
                'success': False,
                'message': 'Failed to generate new OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Send new OTP via email
        if not firebase_service.send_otp_email(email, otp):
            return Response({
                'success': False,
                'message': 'Failed to send OTP email'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'message': 'New OTP sent successfully to your email'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in resend_otp: {e}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
