import base64
import os
import shutil
from typing import Optional
from attr import define, field
from click import echo


@define
class AppPackager:
    app_directory: str = field(kw_only=True)

    def __attrs_post_init__(self):
        self.app_directory = os.path.abspath(self.app_directory)

    @app_directory.validator
    def validate_app_directory(self, _, app_directory: str) -> None:
        if not os.path.exists(app_directory) or not os.path.exists(
            os.path.join(app_directory, "app.py")
        ):
            raise ValueError(f"App doesn't exist in directory: {app_directory}")

    def get_deployment_source(self) -> str:
        tmp_dir = zip_file = None

        try:
            tmp_dir = self._create_deployment_tmp_dir()
            zip_file = self._create_deployment_zip_file(tmp_dir)
            return self._get_deployment_source(zip_file)
        except Exception as e:
            echo(f"Unable to create deployment contents: {e}", err=True)
            raise e
        finally:
            self._clean_up_deployment_artifacts(tmp_dir, zip_file)

    def _create_deployment_tmp_dir(self) -> str:
        # Copy to new dir to ignore certain patterns
        ignore_patterns = []
        if os.path.exists(os.path.join(self.app_directory, ".gitignore")):
            with open(os.path.join(self.app_directory, ".gitignore"), "r") as file:
                for line in file.readlines():
                    if line.endswith("\n"):
                        line = line[:-1]
                    ignore_patterns.append(line.strip())
        return shutil.copytree(
            self.app_directory,
            os.path.join(self.app_directory, "zip_tmp"),
            ignore=shutil.ignore_patterns(*ignore_patterns),
        )

    def _create_deployment_zip_file(self, tmp_dir: str) -> str:
        zip = shutil.make_archive("artifact", "zip", tmp_dir)
        shutil.move(zip, self.app_directory)
        return os.path.join(self.app_directory, "artifact.zip")

    def _get_deployment_source(self, zip_file: str) -> str:
        with open(zip_file, "rb") as file:
            file_data = file.read()

        source = base64.b64encode(file_data).decode("utf-8")
        return source

    def _clean_up_deployment_artifacts(
        self, tmp_dir: Optional[str], zip_file: Optional[str]
    ) -> None:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        if zip_file and os.path.exists(zip_file):
            os.remove(zip_file)
