from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User


@receiver(post_save, sender=User)
def new_user_verification(sender, instance, created, **kwargs):
    """
    This function creates a verification code for new users
    """
    if created:
        # create a user name for user
        username = User.add_username()
        instance.username = username
        instance.save()