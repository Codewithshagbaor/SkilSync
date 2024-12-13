# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import User
from user_profile.models import Profile, JobPreference

@receiver(post_save, sender=User, dispatch_uid="create_profile_signal")
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        JobPreference.objects.create(profile=instance.profile)