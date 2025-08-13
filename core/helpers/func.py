import random
import string


def generate_verification_code():
    return "".join(random.choices(string.digits + string.digits, k=4))