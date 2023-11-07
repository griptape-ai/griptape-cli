import os


def get_api_key() -> str:
    api_key = os.environ.get("GRIPTAPE_CLOUD_API_KEY")

    if not api_key:
        raise ValueError("Missing Griptape Cloud API key!")
    else:
        return api_key
