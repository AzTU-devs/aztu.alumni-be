import re

def is_valid_email(email: str) -> bool:
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None


def is_valid_phone(phone: str) -> bool:
    phone_regex = r'^(\+\d{1,3})?\d{10,12}$'
    return re.match(phone_regex, phone) is not None