import tempfile
import pytest
from click.testing import CliRunner
from griptape.artifacts import TextArtifact
from griptape.cli.commands import app


class TestApp:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.drivers.OpenAiPromptDriver.run",
            return_value=TextArtifact("bar")
        )

    def test_new(self):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(app.new, ["FooBar", "-d", temp_dir])
            assert result.exit_code == 0

    def test_run(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            runner.invoke(app.new, ["FooBar"])

            result = runner.invoke(app.run, ["-a", "foo"])

            assert result.exit_code == 0
