from __future__ import annotations

from typing import Optional
from attrs import Factory, define, field
from fastapi import HTTPException
from subprocess import Popen

from .models import Run, Structure


@define
class RunProcess:
    run: Run = field()
    process: Popen = field()


@define
class State:
    _active_structure: Optional[Structure] = field(default=None)
    structures: dict[str, Structure] = field(default=Factory(dict))
    runs: dict[str, RunProcess] = field(default=Factory(dict))

    @property
    def active_structure(self) -> Structure:
        if self._active_structure is None:
            raise HTTPException(status_code=400, detail="Structure not registered")
        else:
            return self._active_structure

    @active_structure.setter
    def active_structure(self, structure: Structure) -> None:
        self._active_structure = structure

    def register_structure(self, structure: Structure) -> None:
        self.structures[structure.structure_id] = structure
        self.active_structure = structure

    def get_structure(self, structure_id: str) -> Structure:
        if structure_id == "active":
            return self.active_structure
        return self.structures[structure_id]
