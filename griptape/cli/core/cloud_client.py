import json
import os
import stat
from typing import Optional
import requests
from requests import Response
from requests.compat import urljoin
from attr import Factory, define, field

from griptape.cli.core.utils.auth import get_api_key


@define
class CloudClient:
    api_key: Optional[str] = field(kw_only=True, default=Factory(lambda: get_api_key()))
    endpoint_url: str = field(kw_only=True)
    profile: str = field(kw_only=True, default="default")

    def __attrs_post_init__(self):
        self.api_key = get_api_key()
        if not self.profile:
            self.profile = "default"

    def _get_profile_path(self) -> str:
        return os.path.expanduser("~/.gtcloud")

    def _does_profiles_file_exists(self) -> bool:
        return os.path.exists(self._get_profile_path())

    def _extract_profile_data_from_local_storage(self) -> any:
        path = self._get_profile_path()

        with open(path, "r") as file:
            data = file.read()
        return json.loads(data)

    def _write_gt_cloud_profile(
        self, profile_name: str, organization_id: str, environment_id: str
    ) -> None:
        path = self._get_profile_path()

        if self._does_profiles_file_exists():
            data = self._extract_profile_data_from_local_storage()
            data[f"{profile_name}"] = {
                "organization_id": organization_id,
                "environment_id": environment_id,
            }
        else:
            data = {
                f"{profile_name}": {
                    "organization_id": organization_id,
                    "environment_id": environment_id,
                }
            }

        with open(path, "w+") as file:
            file.write(json.dumps(data))
        os.chmod(self._get_profile_path(), stat.S_IRUSR | stat.S_IWUSR)

    def _get_authorization_headers(self) -> dict:
        return {"Authorization": f"{get_api_key()}"}

    def list_organizations(self) -> Response:
        url = urljoin(self.endpoint_url, "organizations/")
        return requests.get(url=url, headers=self._get_authorization_headers())

    def list_environments(self, organization_id: str) -> Response:
        url = urljoin(
            self.endpoint_url, f"organizations/{organization_id}/environments"
        )
        return requests.get(url=url, headers=self._get_authorization_headers())

    def list_apps(self, environment_id: str) -> Response:
        url = urljoin(self.endpoint_url, f"environments/{environment_id}/apps")
        return requests.get(url=url, headers=self._get_authorization_headers())

    def create_app(self, app_data: dict, environment_id: Optional[str]):
        if not environment_id:
            profile_data: dict = self._extract_profile_data_from_local_storage()
            profile = profile_data[self.profile]
            if profile:
                environment_id = profile["environment_id"]
            else:
                raise Exception("Environment ID is required")

        url = urljoin(self.endpoint_url, f"environments/{environment_id}/apps")
        return requests.post(
            url=url, json=app_data, headers=self._get_authorization_headers()
        )

    def create_deployment(self, deployment_data: dict, app_id: str):
        url = urljoin(self.endpoint_url, f"apps/{app_id}/deployments")
        return requests.post(
            url=url, json=deployment_data, headers=self._get_authorization_headers()
        )
