import json
import os
import stat
from typing import Optional
from click import echo
import requests
from requests import Response
from requests.compat import urljoin
from attr import Factory, define, field


@define
class CloudClient:
    api_key: Optional[str] = field(kw_only=True, default=None)
    endpoint_url: Optional[str] = field(kw_only=True, default=None)
    profile: str = field(kw_only=True, default="default")
    profile_data: Optional[dict] = field(
        kw_only=True, default=Factory(lambda: CloudClient._init_profile_data())
    )

    def __attrs_post_init__(self):
        if not self.profile:
            self.profile = "default"
        if not self.api_key:
            try:
                self.api_key = self.profile_data[self.profile]["api_key"]
            except Exception:
                echo("Unable to determine API key! Try running 'gt cloud configure'")
                exit(1)
        if not self.endpoint_url:
            try:
                self.endpoint_url = self.profile_data[self.profile]["endpoint_url"]
            except Exception:
                echo(
                    "Unable to determine endpoint URL! Try running 'gt cloud configure'"
                )
                exit(1)

    @classmethod
    def _init_profile_data(cls) -> dict:
        try:
            data = cls._extract_profile_data_from_local_storage()
            return data
        except Exception:
            return {}

    @classmethod
    def _get_profile_path(cls) -> str:
        return os.path.expanduser("~/.gtcloud")

    @classmethod
    def _does_profiles_file_exist(cls) -> bool:
        return os.path.exists(cls._get_profile_path())

    @classmethod
    def _extract_profile_data_from_local_storage(cls) -> any:
        path = cls._get_profile_path()

        with open(path, "r") as file:
            data = file.read()
        return json.loads(data)

    @staticmethod
    def _write_gt_cloud_profile(
        profile_name: str,
        api_key: str,
        organization_id: str,
        environment_id: str,
        endpoint_url: str,
    ) -> None:
        path = CloudClient._get_profile_path()

        if CloudClient._does_profiles_file_exist():
            data = CloudClient._extract_profile_data_from_local_storage()
            data[f"{profile_name}"] = {
                "api_key": api_key,
                "endpoint_url": endpoint_url,
                "organization_id": organization_id,
                "environment_id": environment_id,
            }
        else:
            data = {
                f"{profile_name}": {
                    "api_key": api_key,
                    "endpoint_url": endpoint_url,
                    "organization_id": organization_id,
                    "environment_id": environment_id,
                }
            }

        with open(path, "w+") as file:
            file.write(json.dumps(data))
        os.chmod(CloudClient._get_profile_path(), stat.S_IRUSR | stat.S_IWUSR)

    def _get_authorization_headers(self) -> dict:
        return {"Authorization": f"{self.api_key}"}

    def _send_request(
        self, method: str, url: str, data: Optional[dict] = None
    ) -> Response:
        response = None

        if method == "GET":
            response = requests.get(url=url, headers=self._get_authorization_headers())
        elif method == "POST":
            response = requests.post(
                url=url, json=data, headers=self._get_authorization_headers()
            )
        elif method == "PUT":
            response = requests.put(
                url=url, json=data, headers=self._get_authorization_headers()
            )
        elif method == "DELETE":
            response = requests.delete(
                url=url, headers=self._get_authorization_headers()
            )
        else:
            raise Exception("Invalid method")

        try:
            response.raise_for_status()
        except Exception as e:
            echo(response.json())
            exit(1)
        return response

    def list_organizations(self) -> Response:
        url = urljoin(self.endpoint_url, "organizations/")
        return self._send_request("GET", url)

    def list_environments(self, organization_id: Optional[str]) -> Response:
        if not organization_id:
            try:
                organization_id = self.profile_data[self.profile]["organization_id"]
            except Exception:
                echo("Organization ID is required")
                exit(1)
        url = urljoin(
            self.endpoint_url, f"organizations/{organization_id}/environments"
        )
        return self._send_request("GET", url)

    def list_apps(self, environment_id: str) -> Response:
        if not environment_id:
            try:
                environment_id = self.profile_data[self.profile]["environment_id"]
            except Exception:
                echo("Environment ID is required")
                exit(1)

        url = urljoin(self.endpoint_url, f"environments/{environment_id}/apps")
        return self._send_request("GET", url)

    def create_app(self, app_data: dict, environment_id: Optional[str]):
        if not environment_id:
            try:
                environment_id = self.profile_data[self.profile]["environment_id"]
            except Exception:
                echo("Environment ID is required")
                exit(1)

        url = urljoin(self.endpoint_url, f"environments/{environment_id}/apps")
        return self._send_request("POST", url, app_data)

    def create_deployment(self, deployment_data: dict, app_id: str):
        url = urljoin(self.endpoint_url, f"apps/{app_id}/deployments")
        return self._send_request("POST", url, deployment_data)
