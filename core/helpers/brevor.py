import requests
from django.conf import settings

class BervorApi:

    @classmethod
    def send_email(cls, payload):
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": f"{settings.BREVOR_API_KEY}"
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return response


    @classmethod
    def new_user_verify_email(cls, recipient:str, name:str, email_verification:str):
        verify_email_content = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Your One-Time Password</title>
        <style type="text/css">
            body { margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; }
            table { border-spacing: 0; }
            table td { border-collapse: collapse; }
            img { -ms-interpolation-mode: bicubic; border: 0; }
            a { color: #3498db; text-decoration: none; }
            .otp-box { background-color: #f6f6f6; border: 1px dashed #cccccc; border-radius: 5px; padding: 15px 25px; text-align: center; }
            .otp-code { font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333333; }
        </style>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f6f6f6; font-family: sans-serif;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
            <td align="center" style="padding: 20px 0;">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="border-collapse: collapse; border: 1px solid #cccccc;">
                <tr>
                    <td align="center" style="padding: 40px 0 30px 0; background-color: #ffffff;">
                    <img src="https://via.placeholder.com/200x50.png?text=Your+Logo" alt="Your Logo" width="200" style="display: block;" />
                    </td>
                </tr>
                <tr>
                    <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                        <tr>
                        <td style="color: #153643; font-family: sans-serif; font-size: 24px; padding-bottom: 20px; font-weight: bold;">
                            Verify your email address
                        </td>
                        </tr>
                        <tr>
                        <td style="color: #153643; font-family: sans-serif; font-size: 16px; line-height: 24px; padding-bottom: 20px;">
                            Hi [Recipient Name],
                            <br/><br/>
                            Please use the following one-time password (OTP) to complete your verification process.
                        </td>
                        </tr>
                        <tr>
                        <td align="center" style="padding: 20px 0;">
                            <div class="otp-box">
                            <span class="otp-code">**[OTP_CODE]**</span>
                            </div>
                        </td>
                        </tr>
                        <tr>
                        <td style="color: #153643; font-family: sans-serif; font-size: 14px; line-height: 20px; padding-top: 20px;">
                            This code is valid for **[EXPIRY_MINUTES]** minutes. For security reasons, do not share this code with anyone.
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                <tr>
                    <td bgcolor="#ee4c50" style="padding: 30px 30px 30px 30px; text-align: center;">
                    <span style="color: #ffffff; font-family: sans-serif; font-size: 14px;">&reg; [Your Company], 2025</span>
                    </td>
                </tr>
                </table>
            </td>
            </tr>
        </table>
        </body>
        </html>
        """
        verify_email_content = verify_email_content.replace("[Recipient Name]", name)
        verify_email_content = verify_email_content.replace("[OTP_CODE]", email_verification)
        verify_email_content = verify_email_content.replace("[EXPIRY_MINUTES]", "10")

        payload = {
            "sender": {
                "name": "QGlide",
                "email": "qglideapp@gmail.com"
            },
            "replyTo": { "email": "qglideapp@gmail.com" },
            "to": [{ "email": recipient }],
            "subject": "email verification",
            "textContent": "test",
            "htmlContent": verify_email_content
        }
        cls.send_email(payload)
        return True