import os
from typing import Optional
import stringcase
from attr import define, field
from cookiecutter.main import cookiecutter


@define
class App:
    DEFAULT_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "app")

    name: str = field(kw_only=True)
    package_manager: str = field(kw_only=True)
    template_path: Optional[str] = field(default=None, kw_only=True)

    def generate(self, directory: str = ".") -> None:
        template = self.DEFAULT_TEMPLATE_PATH if self.template_path is None else self.template_path

        cookiecutter(
            template,
            no_input=True,
            output_dir=directory,
            extra_context={
                "app_name": self.name,
                "package_name": stringcase.snakecase(self.name),
                "package_manager": self.package_manager
            },
        )
