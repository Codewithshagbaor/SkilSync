
from rest_framework import serializers
from web3 import Web3
from .models import Profile, JobPreference, JobMatch
from .utils import upload_to_pinata

class WalletConnectionSerializer(serializers.Serializer):
    wallet_address = serializers.CharField(max_length=42)

    def validate_wallet_address(self, value):
        if not Web3.is_address(value):
            raise serializers.ValidationError("Invalid Ethereum wallet address")
        return value.lower()  # Convert to lowercase for consistency


class ProfileSerializer(serializers.ModelSerializer):
    resume = serializers.URLField(required=False, allow_blank=True)
    class Meta:
        model = Profile
        fields = ['github_url', 'linkedin_url', 'resume', 'skills', 'experience']
    def validate_resume(self, value):
            # If the resume is uploaded via Pinata, it will be a URL
            if value and not value.startswith('https://gateway.pinata.cloud/ipfs/'):
                raise serializers.ValidationError("Invalid resume URL")
            return value

class JobPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPreference
        fields = ['desired_roles', 'work_type', 'salary_range', 'availability']

    def validate_desired_roles(self, value):
            if not isinstance(value, str):
                raise serializers.ValidationError("Desired roles must be a comma-separated string.")
            roles = [role.strip() for role in value.split(',') if role.strip()]
            if not all(isinstance(role, str) for role in roles):
                raise serializers.ValidationError("Each role must be a valid string.")
            return value
    
class JobMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobMatch
        fields = ['job_id', 'job_name', 'job_type', 'job_description', 'company_name', 'location', 'job_url', 'match_score', 'created_at']