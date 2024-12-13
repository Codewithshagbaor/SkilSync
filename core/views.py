from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import *
from .validators import validate_user_data
from core.models import User
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
import secrets
from web3 import Web3
import logging
logger = logging.getLogger(__name__)
class UserCreateView(APIView):
    def post(self, request):
        data = request.data
        errors = validate_user_data(data)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'success': True,
                'status': 200,
                'message': 'User registered successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'success':True,'status':200,'message':'User logged out successfully'},status =status.HTTP_200_OK)
        except Exception as e:
            return Response({'success':False,'status':400,'message': str(e) },status =status.HTTP_400_BAD_REQUEST)
        
def generate_nonce():
    """Generate a secure random nonce"""
    return secrets.token_hex(16)

class WalletLoginView(APIView):
    def post(self, request):
        wallet_address = request.data.get("wallet_address")
        if not wallet_address:
            return Response({"error": "Wallet address is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            formatted_wallet_address = Web3.to_checksum_address(wallet_address)
        except ValueError:
            return Response({"error": "Invalid wallet address"}, status=status.HTTP_400_BAD_REQUEST)

        email = f"{formatted_wallet_address.lower()}@skillsync.xyz"
        username = email.split("@")[0]

        try:
            user_instance, created = User.objects.update_or_create(
                wallet_address=formatted_wallet_address,
                defaults={"email": email, "name": username, "nonce": generate_nonce()}
            )
        except Exception as e:
            logger.error(f"Error creating or updating user: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user_instance)
        return Response({
            "message": "Login successful",
            "wallet_address": formatted_wallet_address,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

            