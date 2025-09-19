from mailersend import emails
from django.conf import settings

class MailerSendApi:

    @classmethod
    def new_user_verify_email(recipient:str, name:str, email_verification:str):
        
        mailer = emails.NewEmail(settings.MAILERSEND_API_KEY)

        # define an empty dict to populate with mail values
        mail_body = {}

        mail_from = {
            "name": "Qglide",
            "email": settings.MAILERSEND_DOMAIN,
        }

        recipients = [
            {
                "name": name,
                "email": recipient,
            }
        ]

        personalization = [
            {
                "email": recipient,
                "data": {
                    "name": name,
                    "otp_code": email_verification
                }
            }
        ]

        reply_to = {
            "name": "QGlide",
            "email": "qglideapp@gmail.com",
        }

        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject("EMAIL VERIFICATION", mail_body)
        mailer.set_template("0r83ql3omz0lzw1j", mail_body)
        mailer.set_advanced_personalization(personalization, mail_body)
        mailer.set_reply_to(reply_to, mail_body)
        print(mailer.send(mail_body))
        return "EMAIL SENT"