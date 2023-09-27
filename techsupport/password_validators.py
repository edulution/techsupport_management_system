from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


# Create a base class for password validators.
class BasePasswordValidator:
    def __init__(self, error_code, error_message):
        # Set the code and message used for reporting errors.
        self.error_code = error_code
        self.error_message = error_message

    # All subclasses must provide a way to check passwords.
    def validate(self, password, user=None):
        raise NotImplementedError("Subclasses must provide a way to check passwords.")

    # Get a helpful message explaining the validation rule.
    def get_help_text(self):
        return self.error_message


# Create a validator to check if a password has the right length.
class MinMaxCharactersValidator(BasePasswordValidator):
    def __init__(self, min_length=8, max_length=13):
        # Define an error message with placeholders for minimum and maximum lengths.
        error_message = _(
            f"Your password must be between {min_length} and {max_length} characters long."
        )
        super().__init__("password_length", error_message)
        self.min_length = min_length
        self.max_length = max_length

    # Check if the password length is within the specified range.
    def validate(self, password, user=None):
        if not self.min_length <= len(password) <= self.max_length:
            raise ValidationError(
                self.error_message,
                code=self.error_code,
                params={"min": self.min_length, "max": self.max_length},
            )


# Create a validator to look for disallowed characters in the password.
class DisallowedCharactersValidator(BasePasswordValidator):
    def __init__(self, disallowed_chars=r'[!@#$%^&*()_+={}[\]:;"\'<>,.?/\\|]'):
        # Define an error message for disallowed characters.
        error_message = _(
            "Your password must not contain characters that are not allowed."
        )
        super().__init__("password_disallowed_characters", error_message)
        self.disallowed_chars = disallowed_chars

    # Check if the password contains any disallowed characters.
    def validate(self, password, user=None):
        if re.search(self.disallowed_chars, password):
            raise ValidationError(
                self.error_message,
                code=self.error_code,
            )


# Create a validator to enforce password strength requirements.
class PasswordStrengthValidator(BasePasswordValidator):
    def __init__(self):
        # Define an error message for password strength requirements.
        error_message = _(
            "Your password must include at least one uppercase letter, one lowercase letter, and one digit."
        )
        super().__init__("password_strength", error_message)

    # Check if the password meets the strength requirements.
    def validate(self, password, user=None):
        if (
            not any(c.isupper() for c in password)
            or not any(c.islower() for c in password)
            or not any(c.isdigit() for c in password)
        ):
            raise ValidationError(
                self.error_message,
                code=self.error_code,
            )
