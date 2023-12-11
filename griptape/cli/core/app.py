import os
from typing import Optional
import stringcase
from attr import define, field
from cookiecutter.main import cookiecutter

from griptape.cli.core.utils.constants import GRIPTAPE_VERSION


@define
class App:
    DEFAULT_TEMPLATE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "templates", "app"
    )

    name: str = field(kw_only=True)
    package_manager: str = field(kw_only=True)
    template_path: Optional[str] = field(default=None, kw_only=True)
    griptape_version: Optional[str] = field(default=None, kw_only=True)

    def generate(self, directory: str = ".") -> None:
        template = (
            self.DEFAULT_TEMPLATE_PATH
            if self.template_path is None
            else self.template_path
        )

        if not self.griptape_version:
            if self.package_manager == "pip":
                self.griptape_version = f">={GRIPTAPE_VERSION}"
            else:
                self.griptape_version = f'"^{GRIPTAPE_VERSION}"'
        else:
            if self.package_manager == "pip":
                self.griptape_version = f"=={self.griptape_version}"
            else:
                self.griptape_version = f'"{self.griptape_version}"'

        cookiecutter(
            template,
            no_input=True,
            output_dir=directory,
            extra_context={
                "app_name": self.name,
                "package_name": stringcase.snakecase(self.name),
                "package_manager": self.package_manager,
                "griptape_version": self.griptape_version,
            },
        )
