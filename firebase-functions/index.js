const functions = require('firebase-functions');
const admin = require('firebase-admin');
const nodemailer = require('nodemailer');

// Initialize Firebase Admin
admin.initializeApp();

// Create a transporter for sending emails
const transporter = nodemailer.createTransporter({
  service: 'gmail',
  auth: {
    user: functions.config().gmail.user,
    pass: functions.config().gmail.password
  }
});

// Cloud Function to send OTP email
exports.sendOTPEmail = functions.https.onCall(async (data, context) => {
  const { email, otp, name } = data;
  
  try {
    // Store OTP in Firestore
    await admin.firestore().collection('otps').doc(email).set({
      otp: otp,
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      expires_at: admin.firestore.FieldValue.serverTimestamp() + (10 * 60 * 1000), // 10 minutes
      used: false,
      attempts: 0
    });

    // Send email with OTP
    const mailOptions = {
      from: 'QGlide <noreply@qglide.com>',
      to: email,
      subject: 'QGlide - Email Verification Code',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #333;">Email Verification</h2>
          <p>Hi ${name || 'User'},</p>
          <p>Your email verification code is:</p>
          <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
            ${otp}
          </div>
          <p>This code will expire in 10 minutes.</p>
          <p>If you didn't request this code, please ignore this email.</p>
          <p>Best regards,<br>QGlide Team</p>
        </div>
      `
    };

    await transporter.sendMail(mailOptions);
    
    return { success: true, message: 'OTP sent successfully' };
  } catch (error) {
    console.error('Error sending OTP email:', error);
    throw new functions.https.HttpsError('internal', 'Failed to send OTP email');
  }
});

// Cloud Function to verify OTP
exports.verifyOTP = functions.https.onCall(async (data, context) => {
  const { email, otp } = data;
  
  try {
    const otpDoc = await admin.firestore().collection('otps').doc(email).get();
    
    if (!otpDoc.exists) {
      throw new functions.https.HttpsError('not-found', 'OTP not found');
    }
    
    const otpData = otpDoc.data();
    
    if (otpData.used) {
      throw new functions.https.HttpsError('already-exists', 'OTP already used');
    }
    
    if (Date.now() > otpData.expires_at.toMillis()) {
      throw new functions.https.HttpsError('deadline-exceeded', 'OTP expired');
    }
    
    if (otpData.otp !== otp) {
      // Increment attempts
      await admin.firestore().collection('otps').doc(email).update({
        attempts: admin.firestore.FieldValue.increment(1)
      });
      throw new functions.https.HttpsError('invalid-argument', 'Invalid OTP');
    }
    
    // Mark OTP as used
    await admin.firestore().collection('otps').doc(email).update({
      used: true
    });
    
    return { success: true, message: 'OTP verified successfully' };
  } catch (error) {
    console.error('Error verifying OTP:', error);
    throw error;
  }
});
