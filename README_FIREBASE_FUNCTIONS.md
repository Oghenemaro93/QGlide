# Firebase Cloud Functions for OTP

This directory contains Firebase Cloud Functions to handle OTP email sending and verification.

## Setup

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
```

### 2. Login to Firebase
```bash
firebase login
```

### 3. Initialize Firebase Functions
```bash
cd firebase-functions
npm install
```

### 4. Configure Gmail (for email sending)
```bash
firebase functions:config:set gmail.user="your-email@gmail.com"
firebase functions:config:set gmail.password="your-app-password"
```

### 5. Deploy Functions
```bash
firebase deploy --only functions
```

## Functions

### sendOTPEmail
- **Trigger**: HTTPS callable function
- **Purpose**: Sends OTP email to user
- **Parameters**: `{ email, otp, name }`
- **Returns**: `{ success: true, message: 'OTP sent successfully' }`

### verifyOTP
- **Trigger**: HTTPS callable function
- **Purpose**: Verifies OTP code
- **Parameters**: `{ email, otp }`
- **Returns**: `{ success: true, message: 'OTP verified successfully' }`

## Usage

### From Django Backend
```python
from firebase_admin import functions

# Get the function reference
send_otp_func = functions.functions().httpsCallable('sendOTPEmail')

# Call the function
result = send_otp_func({
    'email': 'user@example.com',
    'otp': '123456',
    'name': 'John Doe'
})
```

### From Frontend (JavaScript)
```javascript
import { getFunctions, httpsCallable } from 'firebase/functions';

const functions = getFunctions();
const sendOTP = httpsCallable(functions, 'sendOTPEmail');

// Send OTP
const result = await sendOTP({
    email: 'user@example.com',
    otp: '123456',
    name: 'John Doe'
});
```

## Security Rules

The Firestore rules allow:
- Authenticated users to read/write OTP documents
- Users to read their own OTP document

## Environment Variables

Set these in Firebase Functions config:
- `gmail.user`: Gmail address for sending emails
- `gmail.password`: Gmail app password

## Testing

### Local Testing
```bash
firebase emulators:start --only functions
```

### Test Function
```bash
curl -X POST http://localhost:5001/qglide-firebase/us-central1/sendOTPEmail \
  -H "Content-Type: application/json" \
  -d '{"data": {"email": "test@example.com", "otp": "123456", "name": "Test User"}}'
```

## Production Deployment

1. Deploy functions: `firebase deploy --only functions`
2. Update Django backend to use Cloud Functions
3. Configure proper Gmail credentials
4. Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **Gmail Authentication**
   - Enable 2-factor authentication
   - Generate app password
   - Use app password in config

2. **Function Timeout**
   - Increase timeout in function configuration
   - Optimize email sending logic

3. **Firestore Permissions**
   - Check security rules
   - Verify user authentication

### Logs
```bash
firebase functions:log
```

## Next Steps

1. Deploy Firebase Functions
2. Update Django backend to use Cloud Functions
3. Test OTP flow end-to-end
4. Monitor function performance
5. Set up alerts for failures
