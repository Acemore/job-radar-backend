import ipaddress
import re

import phonenumbers

MASK_IP = "[MASKED_IP]"
MASK_EMAIL = "[MASKED_EMAIL]"
MASK_PATH = "[MASKED_PATH]"
MASK_PHONE = "[MASKED_PHONE]"

IPV4_CANDIDATE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
IPV6_CANDIDATE = re.compile(r"\b([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}\b")
EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
GH_ASSET_PATTERN = re.compile(
    r"(\/assets\/)[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"
)
WIN_PATH_PATTERN = re.compile(r"\b[a-zA-Z]:\\Users\\[a-zA-Z0-9_-]+[^\s]*")
LINUX_PATH_PATTERN = re.compile(r"\/home\/[a-zA-Z0-9_-]+[^\s]*")


def sanitize_text(text: str) -> str:
    if not text:
        return text

    for match in IPV4_CANDIDATE.finditer(text):
        ip_str = match.group()
        try:
            ipaddress.ip_address(ip_str)
            text = text.replace(ip_str, MASK_IP)
        except ValueError:
            continue

    for match in IPV6_CANDIDATE.finditer(text):
        ip_str = match.group()
        if "::" in ip_str or ip_str.count(":") >= 2:
            try:
                ipaddress.ip_address(ip_str)
                text = text.replace(ip_str, MASK_IP)
            except ValueError:
                continue

    text = EMAIL_PATTERN.sub(MASK_EMAIL, text)
    text = GH_ASSET_PATTERN.sub(r"\1[MASKED_GUID]", text)
    text = WIN_PATH_PATTERN.sub(MASK_PATH, text)
    text = LINUX_PATH_PATTERN.sub(MASK_PATH, text)

    for match in phonenumbers.PhoneNumberMatcher(text, "RU"):
        text = text.replace(match.raw_string, MASK_PHONE)  # type: ignore

    return text


if __name__ == "__main__":
    test_text = (
        "Connect to 198.51.100.42 or 2001:db8:85a3::8a2e:370:7334. "
        "Do not mask time 14:30 or scipy version 1.250.314.9. "
        "And you will not see email here - my-mail.test@gmail.com. "
        "Image src is https://github.com/user-attachments/assets/b3f71c4a-6d2a"
        "-41e9-9fa2-8cb2586df683 to test link. "
        "Keys are in C:\\Users\\random_user\\info\\keys "
        "Project root is /home/random_developer/random_project "
        "Call me at +7 (999) 123-45-67 or 89101234567."
    )
    print("🚀 Original text:")
    print(test_text)

    print("\n🟢 Sanitized output:")
    print(sanitize_text(test_text))
