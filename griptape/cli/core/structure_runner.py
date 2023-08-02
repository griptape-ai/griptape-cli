import os
import subprocess
import sys
from typing import Optional
from attr import Factory, define, field


@define
class StructureRunner:

    arg: list[str] = field(kw_only=True)
    app_directory: Optional[str] = field(kw_only=True, default=Factory(lambda: os.getcwd()))

    def __attrs_post_init__(self):
        self.app_directory = os.path.abspath(self.app_directory)

    def run(self):
        try:
            sys.path.append(self.app_directory)
            self._install_pip_dependencies()
            from app import init_structure

            try:
                return init_structure().run(*self.arg)
            except Exception as e:
                raise Exception(f"Error running app: {e}")
        except Exception as e:
            raise Exception(f"App doesn't exist: {e}")

    def _install_pip_dependencies(self) -> None:
        requirements_path = os.path.join(self.app_directory, "requirements.txt")
        if os.path.exists(requirements_path):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])