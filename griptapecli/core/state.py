from __future__ import annotations

from attrs import Factory, define, field
from fastapi import HTTPException
from subprocess import Popen

from .models import StructureRun, Structure


@define
class RunProcess:
    run: StructureRun = field()
    process: Popen = field()


@define
class State:
    structures: dict[str, Structure] = field(default=Factory(dict))
    runs: dict[str, RunProcess] = field(default=Factory(dict))

    def register_structure(self, structure: Structure) -> None:
        self.structures[structure.structure_id] = structure

    def get_structure(self, structure_id: str) -> Structure:
        if structure_id in self.structures:
            return self.structures[structure_id]
        else:
            raise HTTPException(status_code=400, detail="Structure not registered")

    def remove_structure(self, structure_id: str) -> str:
        if structure_id in self.structures:
            del self.structures[structure_id]

            return structure_id
        else:
            raise HTTPException(status_code=400, detail="Structure not registered")
