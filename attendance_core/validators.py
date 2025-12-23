from email_validator import validate_email, EmailNotValidError
def is_valid_university_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False
def strong_password(pw: str) -> bool:
    return (len(pw) >= 10 and any(c.islower() for c in pw) and any(c.isupper() for c in pw) and any(c.isdigit() for c in pw) and any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/\\~" for c in pw))
