import random
import string


def correct_password_check(password):
    errors = []

    if not len(password) == 6:
        errors.append("Length must be between 8 digits.")

    if not password.digits():
        errors.append("Must contain only digits.")

    return errors if errors else None


def generate_verification_code():
    return "".join(random.choices(string.digits + string.digits, k=4))