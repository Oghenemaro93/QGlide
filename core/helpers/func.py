import random
import string


def generate_verification_code():
    # For testing purposes, use a fixed OTP code
    return "1234"
    # return "".join(random.choices(string.digits + string.digits, k=4))