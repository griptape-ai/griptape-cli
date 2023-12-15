import os
import subprocess
import sys
from typing import Optional

from attr import Factory, define, field


@define
class StructureRunner:
    args: list[str] = field(kw_only=True)
    init_params: Optional[dict[str, str]] = field(
        kw_only=True, default=Factory(lambda: dict())
    )
    app_directory: Optional[str] = field(
        kw_only=True, default=Factory(lambda: os.getcwd())
    )

    def __attrs_post_init__(self):
        self.app_directory = os.path.abspath(self.app_directory)

    def run(self):
        try:
            os.chdir(self.app_directory)
            sys.path.append(self.app_directory)
            if not self._install_pip_dependencies():
                self._install_poetry_dependencies()
            from app import init_structure

            try:
                return init_structure(*self.args, **self.init_params).run(*self.args)
            except Exception as e:
                raise Exception(f"Error running app: {e}")
        except Exception as e:
            raise Exception(f"Error importing app: {e}")

    def _install_pip_dependencies(self) -> bool:
        requirements_path = os.path.join(self.app_directory, "requirements.txt")
        if os.path.exists(requirements_path):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", requirements_path]
            )
            return True
        return False

    def _install_poetry_dependencies(self) -> None:
        pyproject_path = os.path.join(self.app_directory, "pyproject.toml")
        if os.path.exists(pyproject_path):
            subprocess.check_call(
                ["poetry", "install", "--directory", self.app_directory]
            )
