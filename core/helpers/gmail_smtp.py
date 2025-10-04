from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class GmailSMTP:
    """Gmail SMTP email service for sending OTP emails"""
    
    @classmethod
    def send_otp_email(cls, recipient: str, name: str, otp_code: str) -> bool:
        """
        Send OTP email using Gmail SMTP
        
        Args:
            recipient: Email address to send to
            name: Recipient's name
            otp_code: OTP code to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = "QGlide - Email Verification Code"
            
            # HTML email template with black and yellow theme
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Verification</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        margin: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
                        padding: 30px 20px;
                        text-align: center;
                        position: relative;
                    }}
                    .logo {{
                        max-width: 140px;
                        height: auto;
                        margin-bottom: 10px;
                    }}
                    .header h1 {{
                        margin: 0;
                        color: #FFD700;
                        font-size: 28px;
                        font-weight: 700;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    }}
                    .content {{
                        padding: 40px 30px;
                        background-color: #ffffff;
                    }}
                    .content h2 {{
                        color: #000000;
                        font-size: 24px;
                        margin-bottom: 20px;
                        text-align: center;
                        font-weight: 600;
                    }}
                    .greeting {{
                        color: #333;
                        font-size: 16px;
                        margin-bottom: 20px;
                    }}
                    .otp-box {{
                        background: #000000;
                        border: 2px solid #FFD700;
                        border-radius: 14px;
                        padding: 28px 18px;
                        text-align: center;
                        margin: 28px 0;
                        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
                    }}
                    .otp-code {{
                        font-size: 38px;
                        font-weight: 900;
                        letter-spacing: 10px;
                        color: #FFD700;
                        font-family: 'Courier New', monospace;
                        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
                        margin: 0;
                    }}
                    .otp-label {{
                        color: #000000;
                        font-size: 14px;
                        font-weight: 600;
                        margin-bottom: 10px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #FFD700;
                        border-radius: 6px;
                        padding: 20px;
                        margin: 25px 0;
                        color: #856404;
                        font-size: 14px;
                    }}
                    .warning strong {{
                        color: #000000;
                    }}
                    .footer {{
                        background-color: #000000;
                        padding: 25px 20px;
                        text-align: center;
                        color: #FFD700;
                    }}
                    .footer p {{
                        margin: 5px 0;
                        font-size: 14px;
                    }}
                    .footer .copyright {{
                        color: #cccccc;
                        font-size: 12px;
                    }}
                    .divider {{
                        height: 2px;
                        background: linear-gradient(90deg, #FFD700 0%, #000000 50%, #FFD700 100%);
                        margin: 20px 0;
                    }}
                    .instructions {{
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        border-left: 4px solid #FFD700;
                    }}
                    .instructions h3 {{
                        color: #000000;
                        margin-top: 0;
                        font-size: 16px;
                    }}
                    .instructions ul {{
                        margin: 10px 0;
                        padding-left: 20px;
                    }}
                    .instructions li {{
                        margin: 8px 0;
                        color: #555;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="https://qglide-backend-897216835153.us-central1.run.app/media/images/logo.webp" alt="QGlide Logo" class="logo">
                    </div>
                    
                    <div class="content">
                        <h2>Email Verification</h2>
                        <div class="greeting">
                            <p>Hi <strong>{name}</strong>,</p>
                            <p>Welcome to QGlide! Please use the verification code below to complete your email verification:</p>
                        </div>
                        
                        <div class="otp-box">
                            <div class="otp-label">Verification Code</div>
                            <div class="otp-code">{otp_code}</div>
                        </div>
                        
                        <div class="instructions">
                            <h3>How to use this code:</h3>
                            <ul>
                                <li>Enter this code in the verification field</li>
                                <li>Complete your account setup</li>
                                <li>Start enjoying QGlide services</li>
                            </ul>
                        </div>
                        
                        <div class="warning">
                            <strong>Security Notice:</strong> This code will expire in 10 minutes. Do not share this code with anyone. QGlide will never ask for your verification code via phone or email.
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p style="text-align: center; color: #666; font-size: 14px;">
                            If you didn't request this verification code, please ignore this email or contact our support team.
                        </p>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <strong>Best regards,<br>The QGlide Team</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>QGlide - Your Ride, Your Way</strong></p>
                        <p class="copyright">&copy; 2025 QGlide. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_message = f"""
            QGlide - Email Verification
            
            Hi {name},
            
            Your email verification code is: {otp_code}
            
            This code will expire in 10 minutes. Do not share this code with anyone.
            
            If you didn't request this verification code, please ignore this email.
            
            Best regards,
            The QGlide Team
            
            © 2025 QGlide. All rights reserved.
            """
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"OTP email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {recipient}: {e}")
            return False
    
    @classmethod
    def send_welcome_email(cls, recipient: str, name: str) -> bool:
        """
        Send welcome email after successful verification
        
        Args:
            recipient: Email address to send to
            name: Recipient's name
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = "Welcome to QGlide!"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to QGlide</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        margin: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
                        padding: 30px 20px;
                        text-align: center;
                        position: relative;
                    }}
                    .logo {{
                        max-width: 120px;
                        height: auto;
                        margin-bottom: 15px;
                        filter: brightness(0) invert(1);
                    }}
                    .header h1 {{
                        margin: 0;
                        color: #FFD700;
                        font-size: 28px;
                        font-weight: 700;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    }}
                    .content {{
                        padding: 40px 30px;
                        background-color: #ffffff;
                    }}
                    .content h2 {{
                        color: #000000;
                        font-size: 24px;
                        margin-bottom: 20px;
                        text-align: center;
                        font-weight: 600;
                    }}
                    .greeting {{
                        color: #333;
                        font-size: 16px;
                        margin-bottom: 20px;
                    }}
                    .success-box {{
                        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                        border: 3px solid #000000;
                        border-radius: 12px;
                        padding: 30px 20px;
                        text-align: center;
                        margin: 30px 0;
                        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                    }}
                    .success-icon {{
                        font-size: 48px;
                        color: #000000;
                        margin-bottom: 15px;
                    }}
                    .success-text {{
                        color: #000000;
                        font-size: 18px;
                        font-weight: 700;
                        margin: 0;
                    }}
                    .features {{
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 25px;
                        margin: 25px 0;
                        border-left: 4px solid #FFD700;
                    }}
                    .features h3 {{
                        color: #000000;
                        margin-top: 0;
                        font-size: 18px;
                        margin-bottom: 15px;
                    }}
                    .features ul {{
                        margin: 0;
                        padding-left: 20px;
                    }}
                    .features li {{
                        margin: 10px 0;
                        color: #555;
                        font-size: 14px;
                    }}
                    .footer {{
                        background-color: #000000;
                        padding: 25px 20px;
                        text-align: center;
                        color: #FFD700;
                    }}
                    .footer p {{
                        margin: 5px 0;
                        font-size: 14px;
                    }}
                    .footer .copyright {{
                        color: #cccccc;
                        font-size: 12px;
                    }}
                    .divider {{
                        height: 2px;
                        background: linear-gradient(90deg, #FFD700 0%, #000000 50%, #FFD700 100%);
                        margin: 20px 0;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                        color: #000000;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 700;
                        font-size: 16px;
                        border: 2px solid #000000;
                        margin: 20px 0;
                        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.3);
                    }}
                    .cta-button:hover {{
                        background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="https://qglide-backend-897216835153.us-central1.run.app/media/images/logo.webp" alt="QGlide Logo" class="logo">
                        <h1>QGlide</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Welcome to QGlide!</h2>
                        <div class="greeting">
                            <p>Hi <strong>{name}</strong>,</p>
                            <p>Congratulations! Your email has been successfully verified and your QGlide account is now active.</p>
                        </div>
                        
                        <div class="success-box">
                            <div class="success-icon">🎉</div>
                            <div class="success-text">Your account is ready to use!</div>
                        </div>
                        
                        <div class="features">
                            <h3>What you can do now:</h3>
                            <ul>
                                <li>🚗 Book rides with verified drivers</li>
                                <li>📍 Track your rides in real-time</li>
                                <li>💳 Secure payment processing</li>
                                <li>⭐ Rate and review your experience</li>
                                <li>🔔 Get notifications about your rides</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="https://qglide-backend-897216835153.us-central1.run.app/" class="cta-button">
                                Start Your First Ride
                            </a>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p style="text-align: center; color: #666; font-size: 14px;">
                            Thank you for choosing QGlide. We're excited to have you on board!
                        </p>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <strong>Best regards,<br>The QGlide Team</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>QGlide - Your Ride, Your Way</strong></p>
                        <p class="copyright">&copy; 2025 QGlide. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
            Welcome to QGlide!
            
            Hi {name},
            
            Congratulations! Your email has been successfully verified.
            You can now enjoy all the features of QGlide.
            
            Thank you for joining us!
            
            Best regards,
            The QGlide Team
            
            © 2025 QGlide. All rights reserved.
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Welcome email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {recipient}: {e}")
            return False
    
    @classmethod
    def send_password_reset_email(cls, recipient: str, name: str, reset_link: str) -> bool:
        """
        Send password reset email with reset link
        
        Args:
            recipient: Email address to send to
            name: Recipient's name
            reset_link: Password reset link
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = "QGlide - Password Reset Request"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        margin: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
                        padding: 30px 20px;
                        text-align: center;
                        position: relative;
                    }}
                    .logo {{
                        max-width: 140px;
                        height: auto;
                        margin-bottom: 10px;
                    }}
                    .header h1 {{
                        margin: 0;
                        color: #FFD700;
                        font-size: 28px;
                        font-weight: 700;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    }}
                    .content {{
                        padding: 40px 30px;
                        background-color: #ffffff;
                    }}
                    .content h2 {{
                        color: #000000;
                        font-size: 24px;
                        margin-bottom: 20px;
                        text-align: center;
                        font-weight: 600;
                    }}
                    .greeting {{
                        color: #333;
                        font-size: 16px;
                        margin-bottom: 20px;
                    }}
                    .reset-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                        color: #000000;
                        padding: 18px 35px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 700;
                        font-size: 16px;
                        border: 2px solid #000000;
                        margin: 25px 0;
                        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                        text-align: center;
                        transition: all 0.3s ease;
                    }}
                    .reset-button:hover {{
                        background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border-left: 4px solid #FFD700;
                        border-radius: 6px;
                        padding: 20px;
                        margin: 25px 0;
                        color: #856404;
                        font-size: 14px;
                    }}
                    .warning strong {{
                        color: #000000;
                    }}
                    .footer {{
                        background-color: #000000;
                        padding: 25px 20px;
                        text-align: center;
                        color: #FFD700;
                    }}
                    .footer p {{
                        margin: 5px 0;
                        font-size: 14px;
                    }}
                    .footer .copyright {{
                        color: #cccccc;
                        font-size: 12px;
                    }}
                    .divider {{
                        height: 2px;
                        background: linear-gradient(90deg, #FFD700 0%, #000000 50%, #FFD700 100%);
                        margin: 20px 0;
                    }}
                    .instructions {{
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        border-left: 4px solid #FFD700;
                    }}
                    .instructions h3 {{
                        color: #000000;
                        margin-top: 0;
                        font-size: 16px;
                    }}
                    .instructions ol {{
                        margin: 10px 0;
                        padding-left: 20px;
                    }}
                    .instructions li {{
                        margin: 8px 0;
                        color: #555;
                    }}
                    .link-fallback {{
                        background-color: #e9ecef;
                        border-radius: 6px;
                        padding: 15px;
                        margin: 20px 0;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        color: #495057;
                        word-break: break-all;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <img src="https://qglide-backend-897216835153.us-central1.run.app/media/images/logo.webp" alt="QGlide Logo" class="logo">
                        <h1>QGlide</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Password Reset Request</h2>
                        <div class="greeting">
                            <p>Hi <strong>{name}</strong>,</p>
                            <p>We received a request to reset your password for your QGlide account. Click the button below to reset your password:</p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="reset-button">
                                Reset My Password
                            </a>
                        </div>
                        
                        <div class="instructions">
                            <h3>How to reset your password:</h3>
                            <ol>
                                <li>Click the "Reset My Password" button above</li>
                                <li>Enter your new password on the reset page</li>
                                <li>Confirm your new password</li>
                                <li>Click "Update Password" to complete the process</li>
                            </ol>
                        </div>
                        
                        <div class="warning">
                            <strong>Security Notice:</strong> This link will expire in 1 hour for your security. If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p style="text-align: center; color: #666; font-size: 14px;">
                            If the button doesn't work, you can copy and paste this link into your browser:
                        </p>
                        
                        <div class="link-fallback">
                            {reset_link}
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <strong>Best regards,<br>The QGlide Team</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>QGlide - Your Ride, Your Way</strong></p>
                        <p class="copyright">&copy; 2025 QGlide. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
            QGlide - Password Reset Request
            
            Hi {name},
            
            We received a request to reset your password for your QGlide account.
            
            To reset your password, click on this link:
            {reset_link}
            
            This link will expire in 1 hour for your security.
            
            If you didn't request a password reset, please ignore this email and your password will remain unchanged.
            
            Best regards,
            The QGlide Team
            
            © 2025 QGlide. All rights reserved.
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Password reset email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {recipient}: {e}")
            return False