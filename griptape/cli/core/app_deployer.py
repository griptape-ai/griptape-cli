import os
import shutil
from typing import Optional
import requests
from requests.compat import urljoin
from attr import define, field
from click import echo

from griptape.cli.core.utils.auth import get_auth_token


@define
class AppDeployer:
    app_directory: str = field(kw_only=True)
    endpoint_url: str = field(kw_only=True)
    name: Optional[str] = field(kw_only=True, default=None)

    def __attrs_post_init__(self):
        self.app_directory = os.path.abspath(self.app_directory)

    @app_directory.validator
    def validate_app_directory(self, _, app_directory: str) -> None:
        if not os.path.exists(app_directory) or not os.path.exists(
            os.path.join(app_directory, "app.py")
        ):
            raise ValueError(f"App doesn't exist in directory: {app_directory}")

    def deploy(self):
        tmp_dir = zip_file = None

        try:
            tmp_dir = self._create_deployment_tmp_dir()
            zip_file = self._create_deployment_zip_file(tmp_dir)
            self._deploy_app(zip_file)
        except Exception as e:
            echo(f"Unable to deploy app: {e}", err=True)
            raise e
        finally:
            self._clean_up_deployment_artifacts(tmp_dir, zip_file)

    def _create_deployment_tmp_dir(self) -> str:
        # Copy to new dir to ignore certain patterns
        # TODO: Should more patterns be ignored?
        return shutil.copytree(
            self.app_directory,
            os.path.join(self.app_directory, "zip_tmp"),
            ignore=shutil.ignore_patterns(".venv*"),
        )

    def _create_deployment_zip_file(self, tmp_dir: str) -> str:
        zip = shutil.make_archive("artifact", "zip", tmp_dir)
        shutil.move(zip, self.app_directory)
        return os.path.join(self.app_directory, "artifact.zip")

    def _deploy_app(self, zip_file: str) -> None:
        url = urljoin(self.endpoint_url, "apps/")
        data = {"name": self.name or os.path.basename(self.app_directory)}
        headers = {
            "Authorization": f"Token {get_auth_token(relogin=False, endpoint_url=self.endpoint_url)}"
        }

        with open(zip_file, "rb") as file:
            files = {"zip_file": file}
            response = requests.post(url=url, data=data, files=files, headers=headers)
        if response.status_code != 201:
            raise Exception("Failed to create App")
        echo(f"Response: {response.text}")

    def _clean_up_deployment_artifacts(
        self, tmp_dir: Optional[str], zip_file: Optional[str]
    ) -> None:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        if zip_file and os.path.exists(zip_file):
            os.remove(zip_file)
