import os
import tempfile
import pytest
from click.testing import CliRunner
from griptape.cli.commands import app
from griptape.cli.core.app_deployer import AppDeployer

class TestAppDeployer:


    @pytest.fixture()
    def mock_get_auth_token(self, mocker):
        yield mocker.patch('griptape.cli.core.app_deployer.get_auth_token', return_value = "1234d86fc71d72fe1ec1234567afaf98a8e442e4")

    @pytest.fixture()
    def mock_requests_post(self, mocker):
        yield mocker.patch('griptape.cli.core.app_deployer.requests.post', return_value = mocker.Mock(status_code=201))

    def test_invalid_app_directory(self):
        with pytest.raises(ValueError):
            AppDeployer(app_directory="/tmp", endpoint_url="localhost:8000/")

    def test_deploy(self, mocker, mock_get_auth_token, mock_requests_post):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            runner.invoke(app.new, ["FooBar", "-d", temp_dir])

            url="http://localhost:8000/"
            app_deployer = AppDeployer(app_directory=os.path.join(temp_dir, "FooBar"), endpoint_url=url)
            app_deployer.deploy()

            args, kwargs = mock_requests_post.call_args
            assert kwargs.get("data") == {"name": "FooBar"}
            assert kwargs.get("url") == f"{url}apps/"
            assert kwargs.get("headers") == {"Authorization": f"Token {mock_get_auth_token.return_value}"}
