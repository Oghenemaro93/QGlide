"""
Firebase service for OTP and authentication functionality
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

try:
    from firebase_admin import auth, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not available")


class FirebaseService:
    """Service class for Firebase operations"""
    
    def __init__(self):
        self.initialized = getattr(settings, 'FIREBASE_INITIALIZED', False) and FIREBASE_AVAILABLE
        if self.initialized:
            self.db = firestore.client()
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def store_otp(self, email: str, otp: str, expiry_minutes: int = 10) -> bool:
        """
        Store OTP in Firebase Firestore with expiration
        
        Args:
            email: User's email address
            otp: Generated OTP code
            expiry_minutes: OTP expiration time in minutes
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Store OTP in Firestore
            doc_ref = self.db.collection('otps').document(email)
            doc_ref.set({
                'otp': otp,
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': firestore.SERVER_TIMESTAMP + timedelta(minutes=expiry_minutes),
                'used': False,
                'attempts': 0
            })
            
            # Also store in Django cache as backup
            cache_key = f"otp_{email}"
            cache.set(cache_key, {
                'otp': otp,
                'expires_at': datetime.now() + timedelta(minutes=expiry_minutes),
                'used': False,
                'attempts': 0
            }, timeout=expiry_minutes * 60)
            
            logger.info(f"OTP stored successfully for {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store OTP for {email}: {e}")
            return False
    
    def verify_otp(self, email: str, provided_otp: str) -> Dict[str, Any]:
        """
        Verify OTP code for email
        
        Args:
            email: User's email address
            provided_otp: OTP code provided by user
            
        Returns:
            dict: Verification result with status and message
        """
        if not self.initialized:
            return {
                'success': False,
                'message': 'Firebase not initialized',
                'error': 'FIREBASE_NOT_INITIALIZED'
            }
        
        try:
            # Try Firestore first
            doc_ref = self.db.collection('otps').document(email)
            doc = doc_ref.get()
            
            if not doc.exists:
                # Fallback to Django cache
                cache_key = f"otp_{email}"
                cached_data = cache.get(cache_key)
                
                if not cached_data:
                    return {
                        'success': False,
                        'message': 'OTP not found or expired',
                        'error': 'OTP_NOT_FOUND'
                    }
                
                # Verify from cache
                if cached_data['used']:
                    return {
                        'success': False,
                        'message': 'OTP already used',
                        'error': 'OTP_ALREADY_USED'
                    }
                
                if datetime.now() > cached_data['expires_at']:
                    return {
                        'success': False,
                        'message': 'OTP expired',
                        'error': 'OTP_EXPIRED'
                    }
                
                if cached_data['otp'] != provided_otp:
                    cached_data['attempts'] += 1
                    cache.set(cache_key, cached_data, timeout=600)  # 10 minutes
                    return {
                        'success': False,
                        'message': 'Invalid OTP',
                        'error': 'INVALID_OTP'
                    }
                
                # Mark as used
                cached_data['used'] = True
                cache.set(cache_key, cached_data, timeout=600)
                
                return {
                    'success': True,
                    'message': 'OTP verified successfully'
                }
            
            # Verify from Firestore
            data = doc.to_dict()
            
            if data['used']:
                return {
                    'success': False,
                    'message': 'OTP already used',
                    'error': 'OTP_ALREADY_USED'
                }
            
            if datetime.now() > data['expires_at']:
                return {
                    'success': False,
                    'message': 'OTP expired',
                    'error': 'OTP_EXPIRED'
                }
            
            if data['otp'] != provided_otp:
                # Increment attempts
                doc_ref.update({'attempts': firestore.Increment(1)})
                return {
                    'success': False,
                    'message': 'Invalid OTP',
                    'error': 'INVALID_OTP'
                }
            
            # Mark as used
            doc_ref.update({'used': True})
            
            # Also mark in cache
            cache_key = f"otp_{email}"
            cache.delete(cache_key)
            
            return {
                'success': True,
                'message': 'OTP verified successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to verify OTP for {email}: {e}")
            return {
                'success': False,
                'message': 'Verification failed',
                'error': 'VERIFICATION_ERROR'
            }
    
    def send_otp_email(self, email: str, otp: str) -> bool:
        """
        Send OTP via Firebase Cloud Functions
        
        Args:
            email: Recipient email address
            otp: OTP code to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Store the OTP in Firestore first
            if not self.store_otp(email, otp):
                return False
            
            # Get user name for email
            from core.models import User
            try:
                user = User.objects.get(email=email)
                name = user.full_name or user.first_name or "User"
            except User.DoesNotExist:
                name = "User"
            
            # Use Gmail SMTP to send OTP email
            try:
                from core.helpers.gmail_smtp import GmailSMTP
                success = GmailSMTP.send_otp_email(recipient=email, name=name, otp_code=otp)
                
                if success:
                    logger.info(f"OTP sent via Gmail SMTP to {email}")
                    return True
                else:
                    logger.error(f"Failed to send OTP via Gmail SMTP to {email}")
                    return False
                
            except Exception as e:
                logger.error(f"Failed to send OTP via Gmail SMTP to {email}: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")
            return False
    
    def generate_email_verification_link(self, email: str) -> Optional[str]:
        """
        Generate Firebase email verification link
        
        Args:
            email: User's email address
            
        Returns:
            str: Verification link or None if failed
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            link = auth.generate_email_verification_link(email)
            return link
        except Exception as e:
            logger.error(f"Failed to generate email verification link for {email}: {e}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> Optional[str]:
        """
        Create custom Firebase token for user
        
        Args:
            uid: User's unique identifier
            additional_claims: Additional claims to include in token
            
        Returns:
            str: Custom token or None if failed
        """
        if not self.initialized:
            logger.error("Firebase not initialized")
            return None
        
        try:
            token = auth.create_custom_token(uid, additional_claims)
            return token.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to create custom token for {uid}: {e}")
            return None


# Global instance
firebase_service = FirebaseService()
