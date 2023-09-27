from django.test import TestCase
from techsupport.password_validators import (
    MinMaxCharactersValidator,
    DisallowedCharactersValidator,
    PasswordStrengthValidator,
)
from django.core.exceptions import ValidationError

# Define a test class for the password validators.
class TestPasswordValidators(TestCase):
    def setUp(self):
        # Initialize the validators
        self.min_max_validator = MinMaxCharactersValidator(min_length=5, max_length=8)
        self.disallowed_char_validator = DisallowedCharactersValidator(disallowed_chars=r'[!@#]')
        self.strength_validator = PasswordStrengthValidator()

    # Test the MinMaxCharactersValidator
    def test_min_max_characters_validator(self):
        # Define valid and invalid passwords for testing.
        valid_password = "VadPwd1"
        invalid_password_short = "Pwd1"
        invalid_password_long = "ThisPasswordIsTooLong1"

        # Test valid password
        self.min_max_validator.validate(valid_password)

        # Test invalid passwords, they should raise ValidationError.
        with self.assertRaises(ValidationError):
            self.min_max_validator.validate(invalid_password_short)
        with self.assertRaises(ValidationError):
            self.min_max_validator.validate(invalid_password_long)

    # Test the DisallowedCharactersValidator
    def test_disallowed_characters_validator(self):
        # Define valid and invalid passwords for testing.
        valid_password = "Pwd123"
        invalid_password = "Pwd@123"

        # Test valid password
        self.disallowed_char_validator.validate(valid_password)

        # Test invalid password, it should raise ValidationError.
        with self.assertRaises(ValidationError):
            self.disallowed_char_validator.validate(invalid_password)

    # Test the PasswordStrengthValidator
    def test_password_strength_validator(self):
        # Define valid and invalid passwords for testing.
        valid_password = "StrgPw3!"
        invalid_password = "weaksord"

        # Test valid password
        self.strength_validator.validate(valid_password)

        # Test invalid password, it should raise ValidationError.
        with self.assertRaises(ValidationError):
            self.strength_validator.validate(invalid_password)
