import secrets
import string

LEN_CODE = 10


def generate_ref_code():
    letters_and_digits = string.ascii_letters + string.digits
    ref_code = ''.join(secrets.choice(
        letters_and_digits) for _ in range(LEN_CODE))
    return ref_code
