import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password
from core.models import User

class UserDataValidator:
    def __init__(self, data):
        self.data = data
        self.errors = {}

    def validate(self):
        self._validate_email()
        self._validate_passwords()
        self._validate_name()
        return self.errors

    def _validate_email(self):
        email = self.data.get('email')
        if not email:
            self.errors['email'] = "Email address is required."
            return

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            self.errors['email'] = "Please enter a valid email address."
            return

        if User.objects.filter(email=email).exists():
            self.errors['email'] = "This email address is already registered."

    def _validate_name(self):
        name = self.data.get('name')
        if not name:
            self.errors['name'] = "Name name is required."
        elif len(name) < 2:
            self.errors['name'] = "Name name must be at least 2 characters long."
    def _validate_passwords(self):
        password = self.data.get('password')
        password_confirm = self.data.get('password_confirm')

        if not password:
            self.errors['password'] = "Password is required."
            return
        
        if not password_confirm:
            self.errors['password_confirm'] = "Password confirmation is required."
            return

        if password != password_confirm:
            self.errors['password_confirm'] = "Passwords do not match."
            return

        try:
            validate_password(password)
        except ValidationError as e:
            self.errors['password'] = list(e.messages)
            return

        if not self._check_password_complexity(password):
            self.errors['password'] = "Password must contain at least one uppercase letter, one lowercase letter, one numeric value, and one of the symbols $@#%&."
    @staticmethod
    def _check_password_complexity(password):
        return (
            re.search(r'\d', password) and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            any(char in "$@#%&" for char in password)
        )

def validate_user_data(data):
    validator = UserDataValidator(data)
    return validator.validate()