import tempfile
import pytest
from click.testing import CliRunner
from griptape.cli.commands import app
from griptape.cli.core.app_deployer import AppDeployer
from griptape.cli.core.structure_runner import StructureRunner


class TestApp:
    @pytest.fixture()
    def mock_structure_runner_instance(self, mocker):
        structure_runner_mock = mocker.Mock(spec=StructureRunner)
        structure_runner_mock.run.return_value = None
        return structure_runner_mock

    @pytest.fixture()
    def mock_structure_runner(self, mocker, mock_structure_runner_instance):
        mocker.patch(
            "griptape.cli.commands.app.StructureRunner",
            return_value=mock_structure_runner_instance,
        )

    @pytest.fixture()
    def mock_app_deployer_instance(self, mocker):
        app_deployer_mock = mocker.Mock(spec=AppDeployer)
        app_deployer_mock.deploy.return_value = None
        return app_deployer_mock

    @pytest.fixture()
    def mock_app_deployer(self, mocker, mock_app_deployer_instance):
        mocker.patch(
            "griptape.cli.commands.app.AppDeployer",
            return_value=mock_app_deployer_instance,
        )

    def test_new(self):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(app.new, ["FooBar", "-d", temp_dir])
            assert result.exit_code == 0

    def test_run(self, mock_structure_runner_instance, mock_structure_runner):
        runner = CliRunner()

        with runner.isolated_filesystem():
            runner.invoke(app.new, ["FooBar"])

            result = runner.invoke(app.run, ["-a", "foo", "-d", "./FooBar"])

            mock_structure_runner_instance.run.assert_called_once()
            assert result.exit_code == 0

    def test_deploy(self, mock_app_deployer_instance, mock_app_deployer):
        runner = CliRunner()

        with runner.isolated_filesystem():
            runner.invoke(app.new, ["FooBar"])

            result = runner.invoke(app.deploy, ["-d", "./FooBar"])

            mock_app_deployer_instance.deploy.assert_called_once()
            assert result.exit_code == 0
