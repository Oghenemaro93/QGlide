# Gmail SMTP Setup for QGlide

This guide explains how to configure Gmail SMTP for sending OTP emails in QGlide.

## Prerequisites

- Gmail account
- 2-Factor Authentication enabled on your Gmail account

## Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click "2-Step Verification"
3. Follow the setup process to enable 2FA

## Step 2: Generate App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "Signing in to Google", click "App passwords"
3. Select "Mail" as the app
4. Select "Other" as the device and enter "QGlide Backend"
5. Click "Generate"
6. Copy the 16-character password (no spaces)

## Step 3: Configure Environment Variables

### For Local Development

Create a `.env` file in your project root:

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=noreply@qglide.com
```

### For Cloud Run Deployment

Update the environment variables in your Cloud Run service:

```bash
gcloud run services update qglide-backend \
    --region us-central1 \
    --set-env-vars EMAIL_HOST_USER=your-email@gmail.com,EMAIL_HOST_PASSWORD=your-16-character-app-password,DEFAULT_FROM_EMAIL=noreply@qglide.com
```

Or update the `deploy.sh` script with your actual values:

```bash
# Replace these values in deploy.sh
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=noreply@qglide.com
```

## Step 4: Test Email Sending

### Test Locally

```bash
cd QGlide
python manage.py shell
```

```python
from core.helpers.gmail_smtp import GmailSMTP

# Test OTP email
success = GmailSMTP.send_otp_email(
    recipient="test@example.com",
    name="Test User",
    otp_code="123456"
)
print(f"Email sent: {success}")
```

### Test via API

1. Start your Django server
2. Use the registration endpoint to test OTP sending
3. Check your email for the OTP

## Configuration Details

### Django Settings

The following settings are configured in `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@qglide.com')
```

### Gmail SMTP Service

The `GmailSMTP` class in `core/helpers/gmail_smtp.py` provides:

- `send_otp_email()` - Send OTP verification emails
- `send_welcome_email()` - Send welcome emails after verification

## Email Templates

### OTP Email Template

- Professional HTML design
- Clear OTP code display
- 10-minute expiration notice
- Security warnings

### Welcome Email Template

- Success confirmation
- Branded design
- Next steps information

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure 2FA is enabled
   - Use app password, not regular password
   - Check app password has no spaces

2. **Connection Error**
   - Verify Gmail SMTP settings
   - Check firewall/network restrictions
   - Ensure port 587 is open

3. **Email Not Received**
   - Check spam folder
   - Verify recipient email address
   - Check Gmail sending limits (500/day)

### Debug Mode

Enable debug logging in Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core.helpers.gmail_smtp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Security Best Practices

1. **Never commit app passwords to version control**
2. **Use environment variables for sensitive data**
3. **Rotate app passwords regularly**
4. **Monitor email sending limits**
5. **Use dedicated email accounts for production**

## Gmail Limits

- **Free Gmail**: 500 emails per day
- **Google Workspace**: 2,000 emails per day
- **Rate limiting**: 100 emails per hour per user

## Alternative Email Services

If you need higher limits, consider:

- **SendGrid**: 100 emails/day free
- **Mailgun**: 5,000 emails/month free (first 3 months)
- **Amazon SES**: 200 emails/day free (with EC2)
- **Resend**: 3,000 emails/month free

## Support

For issues with Gmail SMTP setup:

1. Check Gmail account security settings
2. Verify app password generation
3. Test with a simple email first
4. Check Django logs for error messages
5. Verify environment variables are set correctly
