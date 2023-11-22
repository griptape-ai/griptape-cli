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

            zip_file = shutil.make_archive(
                "artifact", "zip", os.path.join(temp_dir, "FooBar")
            )
            with open(zip_file, "rb") as file:
                file_data = file.read()

            source = base64.b64encode(file_data).decode("utf-8")

            app_deployer = AppPackager(app_directory=os.path.join(temp_dir, "FooBar"))

            ad_source = app_deployer.get_deployment_source()
            assert ad_source == source
