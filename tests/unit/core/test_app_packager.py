import base64
import os
import shutil
import tempfile
import pytest
from click.testing import CliRunner
from griptape.cli.commands import app
from griptape.cli.core.app_packager import AppPackager


class TestAppPackager:
    def test_invalid_app_directory(self):
        with pytest.raises(ValueError):
            AppPackager(app_directory="/tmp")

    def test_deploy(self):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            runner.invoke(app.new, ["FooBar", "-d", temp_dir])

            app_deployer = AppPackager(app_directory=os.path.join(temp_dir, "FooBar"))

            app_source = app_deployer.get_deployment_source()

            os.makedirs(os.path.join(temp_dir, "artifact"))
            dir = os.path.join(temp_dir, "artifact")
            with open(os.path.join(dir, "artifact.zip"), "wb") as f:
                f.write(base64.b64decode(app_source))

            shutil.unpack_archive(os.path.join(dir, "artifact.zip"), dir, "zip")
            files = os.listdir(dir)
            assert "app.py" in files
            assert "requirements.txt" in files
            assert "README.md" in files
            assert ".gitignore" in files
