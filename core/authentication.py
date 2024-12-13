from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class WalletAddressBackend(ModelBackend):
    def authenticate(self, request, wallet_address=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(wallet_address=wallet_address)
            return user
        except UserModel.DoesNotExist:
            return None