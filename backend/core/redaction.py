import re

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+?\b\d[\d\-\s]{8,14}\d\b')


def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text

    def email_repl(m):
        email = m.group(0)
        parts = email.split('@', 1)
        if len(parts) == 2:
            user, domain = parts
            if len(user) > 1:
                user = user[0] + "***"
            else:
                user = "***"
            return f"{user}@{domain}"
        return email

    text = EMAIL_REGEX.sub(email_repl, text)

    def phone_repl(m):
        phone = m.group(0)
        digits = re.sub(r'\D', '', phone)
        # Check if it looks like a real phone number
        if len(digits) >= 10:
            return (
                phone[:-4].replace('0', '*').replace('1', '*').replace('2', '*')
                .replace('3', '*').replace('4', '*').replace('5', '*')
                .replace('6', '*').replace('7', '*').replace('8', '*')
                .replace('9', '*') + phone[-4:]
            )
        return phone

    text = PHONE_REGEX.sub(phone_repl, text)

    text = re.sub(r'\b\d{6}\b', "[REDACTED OTP]", text)

    return text
