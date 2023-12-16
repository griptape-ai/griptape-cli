import re


def is_valid_endpoint(endpoint: str) -> bool:
    if re.match(r"^^https:\/\/api\.cloud(?:\-.*)?\.griptape\.ai$", endpoint):
        return True
    else:
        return False
