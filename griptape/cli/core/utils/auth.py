import json
import os
import stat
from typing import Optional
import requests
from click import echo
from requests.compat import urljoin
from datetime import datetime

from griptape.cli.core.utils.constants import DEFAULT_ENDPOINT_URL


def get_auth_token(relogin: bool, endpoint_url: Optional[str]) -> str:
    if not relogin and _is_token_stored_locally():
        token_data = _extract_token_data_from_local_storage()
        if "token" in token_data:
            return token_data["token"]
    return _retrieve_auth_token(endpoint_url=endpoint_url or DEFAULT_ENDPOINT_URL)


def _retrieve_auth_token(endpoint_url: str) -> str:
    username, password = _get_user_credentials()
    token = _request_access_token(username, password, endpoint_url)
    _write_gt_cloud(username, token)
    return token


def _is_token_stored_locally() -> bool:
    return os.path.exists(os.path.expanduser("~/.gtcloud"))


def _extract_token_data_from_local_storage() -> str:
    path = os.path.expanduser("~/.gtcloud")

    with open(path, "r") as file:
        data = file.read()
    return json.loads(data)


def _get_user_credentials() -> tuple:
    username = os.environ.get("GRIPTAPE_CLOUD_USERNAME")
    password = os.environ.get("GRIPTAPE_CLOUD_PASSWORD")

    if not username or not password:
        raise ValueError("Missing Griptape Cloud credentials!")
    else:
        return (username, password)


def _request_access_token(username: str, password: str, endpoint_url: str) -> str:
    url = urljoin(endpoint_url, "auth-token/")

    data = {"username": username, "password": password}

    try:
        response = requests.post(url=url, data=data)
        if response.status_code != 200:
            raise Exception(f"{response.content.decode(encoding='utf-8')}")
        return response.json()["token"]
    except Exception as err:
        echo(f"{err}")
        raise err


def _write_gt_cloud(username: str, token: str) -> None:
    path = os.path.expanduser("~/.gtcloud")

    data = {
        "username": username,
        "token": token,
        "timestamp": datetime.utcnow().timestamp(),
    }

    with open(path, "w+") as file:
        file.write(json.dumps(data))
    os.chmod(os.path.expanduser("~/.gtcloud"), stat.S_IRUSR | stat.S_IWUSR)
