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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

# Using existing Django OTP system instead of Firebase

logger = logging.getLogger(__name__)
User = get_user_model()


@swagger_auto_schema(
    method='post',
    operation_description="Send OTP to user's email for verification",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='User email address',
                example='user@example.com'
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="OTP sent successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: openapi.Response(description="Bad request - Invalid email or missing email"),
        404: openapi.Response(description="User not found"),
        500: openapi.Response(description="Internal server error")
    }
)
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
        
        # Generate OTP using existing Django system
        from core.helpers.func import generate_verification_code
        
        otp = generate_verification_code()
        
        # Store OTP in user record (existing system)
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        UserModel.hash_otp(otp_code=otp, user=user)
        
        # Send OTP via email using existing Gmail SMTP
        try:
            from core.helpers.gmail_smtp import GmailSMTP
            success = GmailSMTP.send_otp_email(recipient=email, name=user.full_name, otp_code=otp)
            
            if not success:
                return Response({
                    'success': False,
                    'message': 'Failed to send OTP email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
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


@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP code for email verification",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'otp'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='User email address',
                example='user@example.com'
            ),
            'otp': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='6-digit OTP code',
                example='123456'
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="OTP verified successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: openapi.Response(description="Bad request - Invalid OTP, expired, or already used"),
        404: openapi.Response(description="User not found"),
        500: openapi.Response(description="Internal server error")
    }
)
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
        
        # Get user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP using existing Django system
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        valid_otp_code = UserModel.check_otp(user=user, otp_code=otp)
        if valid_otp_code is False:
            return Response({
                'success': False,
                'message': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark user email as verified
        user.is_verified = True
        user.save()
        
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


@swagger_auto_schema(
    method='post',
    operation_description="Resend OTP to user's email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='User email address',
                example='user@example.com'
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="New OTP sent successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: openapi.Response(description="Bad request - Invalid email or missing email"),
        404: openapi.Response(description="User not found"),
        500: openapi.Response(description="Internal server error")
    }
)
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
        
        # Generate new OTP using existing Django system
        from core.helpers.func import generate_verification_code
        
        otp = generate_verification_code()
        
        # Store new OTP in user record (existing system)
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        UserModel.hash_otp(otp_code=otp, user=user)
        
        # Send new OTP via email using existing Gmail SMTP
        try:
            from core.helpers.gmail_smtp import GmailSMTP
            success = GmailSMTP.send_otp_email(recipient=email, name=user.full_name, otp_code=otp)
            
            if not success:
                return Response({
                    'success': False,
                    'message': 'Failed to send OTP email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Failed to send OTP email: {e}")
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
