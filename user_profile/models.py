# models.py
from django.db import models
from core.models import User
from django.utils.translation import gettext_lazy as _

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_url = models.URLField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(max_length=255, blank=True, null=True)
    resume = models.URLField(blank=True, null=True, help_text="IPFS URL of the resume")
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    experience = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated experience")
    
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f"{self.user.username}'s profile"

class JobPreference(models.Model):
    WORK_TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid')
    ]
    
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    desired_roles = models.TextField(blank=True, null=True, help_text="Comma-separated roles")
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES)
    salary_range = models.TextField(blank=True, null=True, help_text="Comma-separated salary range")
    availability = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Job Preference')
        verbose_name_plural = _('Job Preferences')
        
    def __str__(self):
        return f"{self.profile.user.username}'s job preference"
class JobMatch(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255)
    job_name = models.CharField(max_length=255)
    job_type = models.CharField(max_length=255)
    job_description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_url = models.URLField(max_length=255)
    match_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Job Match')
        verbose_name_plural = _('Job Matches')
        
    def __str__(self):
        return f"{self.profile.user.username}'s job match"