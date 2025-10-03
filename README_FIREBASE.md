# Firebase OTP Integration for QGlide

This document explains how to set up Firebase for OTP (One-Time Password) functionality in the QGlide backend.

## Overview

Firebase is integrated to provide:
- OTP generation and storage
- Email verification via OTP
- Secure token management
- Firestore database for OTP storage

## Setup Instructions

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name (e.g., "qglide-firebase")
4. Enable Google Analytics (optional)
5. Create project

### 2. Enable Firestore Database

1. In Firebase Console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a location (preferably same as your Cloud Run region)
5. Click "Done"

### 3. Generate Service Account Key

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase-service-account.json`
5. Place it in your project root directory

### 4. Environment Variables

Add these to your `.env` file or Cloud Run environment:

```bash
FIREBASE_CREDENTIALS_PATH=/app/firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### 5. Cloud Run Deployment

For Cloud Run deployment, you have two options:

#### Option A: Include in Docker Image (Development)
```dockerfile
COPY firebase-service-account.json /app/
```

#### Option B: Use Environment Variables (Production)
Set the service account JSON as an environment variable in Cloud Run:
```bash
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
```

## API Endpoints

### Send OTP
```http
POST /v1/auth/send-otp/
Content-Type: application/json

{
    "email": "user@example.com"
}
```

### Verify OTP
```http
POST /v1/auth/verify-otp/
Content-Type: application/json

{
    "email": "user@example.com",
    "otp": "123456"
}
```

### Resend OTP
```http
POST /v1/auth/resend-otp/
Content-Type: application/json

{
    "email": "user@example.com"
}
```

## Response Format

### Success Response
```json
{
    "success": true,
    "message": "OTP sent successfully to your email"
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error description",
    "error": "ERROR_CODE"
}
```

## Error Codes

- `FIREBASE_NOT_INITIALIZED`: Firebase not properly configured
- `OTP_NOT_FOUND`: OTP not found or expired
- `OTP_ALREADY_USED`: OTP has already been used
- `OTP_EXPIRED`: OTP has expired
- `INVALID_OTP`: Incorrect OTP provided
- `VERIFICATION_ERROR`: General verification error

## Security Features

1. **OTP Expiration**: OTPs expire after 10 minutes
2. **Single Use**: Each OTP can only be used once
3. **Attempt Tracking**: Failed attempts are tracked
4. **Secure Storage**: OTPs stored in Firestore with encryption
5. **Cache Backup**: Django cache used as backup storage

## Testing

### Local Testing
1. Set up Firebase project
2. Download service account key
3. Set environment variables
4. Run Django server
5. Test endpoints with Postman or curl

### Production Testing
1. Deploy to Cloud Run with Firebase credentials
2. Test OTP flow end-to-end
3. Verify email delivery
4. Test OTP verification

## Troubleshooting

### Common Issues

1. **Firebase not initialized**
   - Check service account key path
   - Verify project ID
   - Check environment variables

2. **OTP not sent**
   - Check email service configuration
   - Verify Firebase permissions
   - Check logs for errors

3. **OTP verification fails**
   - Check OTP expiration
   - Verify OTP format
   - Check Firestore permissions

### Logs
Check Django logs for Firebase-related errors:
```bash
# Local
python manage.py runserver

# Cloud Run
gcloud logs read --service=qglide-backend
```

## Security Considerations

1. **Service Account Key**: Keep it secure, never commit to version control
2. **Firestore Rules**: Set up proper security rules for production
3. **Rate Limiting**: Implement rate limiting for OTP requests
4. **Monitoring**: Monitor OTP usage and failed attempts

## Next Steps

1. Set up Firebase project
2. Configure environment variables
3. Test OTP functionality
4. Deploy to Cloud Run
5. Monitor and maintain
lidt oxqt mntl mjwh
{
    "email": "chikezie.ndubuisi01@gmail.com",
    "password": "Test123!",
    "confirm_password": "Test123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567892",
    "country_code": "+1",
    "user_type": "USER"
}