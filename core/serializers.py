from rest_framework import serializers
from core.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar', 'wallet_address', 'nonce', 'is_verified']
        read_only_fields = ['is_verified']

class MyCustomObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        #Display these whenever token is decoded
        token['email'] = user.email

        return token
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, )        
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password_confirm']
        
    # Check if passwords matches
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Password fields does not match'}
            )        
        return attrs 

    # Create a new user
    def create(self, validated_data):
        # email = validated_data['email']
        # email_split = email.split('@')[0]
        # random_id = get_random_string(5, allowed_chars='0123456789')
        # username = f"{email_split.lower()}.{random_id}"

        # Remove password_confirm from the validated data since it's not needed
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data.get('name'),
            password=validated_data['password']
        )
        
        return user
    