import os
import tempfile
import pytest
import unittest
from click.testing import CliRunner
from griptape.tasks import BaseTask
from griptape.cli.commands import app
from griptape.cli.core.structure_runner import StructureRunner


class TestStructureRunner:
    @pytest.fixture()
    def mock_subprocess(self, mocker):
        yield mocker.patch(
            "griptape.cli.core.structure_runner.subprocess.check_call", return_value=0
        )

    def test_run(self, mocker, mock_subprocess):
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            runner.invoke(app.new, ["FooBar", "-d", temp_dir])

            workdir = os.getcwd()
            os.chdir(temp_dir)
            structure_runner = StructureRunner(
                arg=["foo", "bar"], app_directory="./FooBar"
            )
            os.chdir(workdir)

            # Check for substring due to 'private' folder prefix
            assert os.path.join(temp_dir, "FooBar") in structure_runner.app_directory

            mock_task = mocker.Mock(spec=BaseTask)
            mock_app = mocker.Mock()
            mock_structure = mocker.Mock()
            mock_app.init_structure.return_value = mock_structure
            mock_structure.run.return_value = mock_task
            with unittest.mock.patch.dict("sys.modules", app=mock_app):
                result = structure_runner.run()
                assert result == mock_task
                mock_subprocess.assert_called_once()
                args, kwargs = mock_structure.run.call_args
                assert args == ("foo", "bar")
