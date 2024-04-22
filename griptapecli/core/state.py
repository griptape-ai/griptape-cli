from __future__ import annotations

from enum import Enum
from multiprocessing import Manager
from multiprocessing.managers import DictProxy, SyncManager
from typing import Optional

import psutil
from attrs import Factory, define, field
from fastapi import HTTPException

from .models import Run, Structure


@define
class RunProcess:
    class ProcessStatus(Enum):
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    run: Run = field()
    pid: int = field()
    _process_status: Optional[int] = field(default=None)

    @property
    def process_status(self) -> Optional[int]:
        if self._process_status is None:
            try:
                process = psutil.Process(self.pid)
                if process.is_running():
                    if process.status() == psutil.STATUS_ZOMBIE:
                        print("Zombie process detected")
                        self._process_status = process.wait(timeout=30)
                        print(
                            f"Process {self.pid} exited with status {self._process_status}"
                        )
            except psutil.NoSuchProcess:
                pass

        return self._process_status


@define
class State:
    manager: SyncManager = field(default=Factory(Manager))
    store: DictProxy = field(
        default=Factory(lambda self: self.manager.dict(), takes_self=True)
    )

    @property
    def structures(self) -> dict[str, Structure]:
        if "structures" not in self.store:
            self.store["structures"] = self.manager.dict()
        return self.store["structures"]

    @property
    def runs(self) -> dict[str, Run]:
        if "runs" not in self.store:
            self.store["runs"] = self.manager.dict()
        return self.store["runs"]

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

    def update_run(self, run_id: str, values: dict) -> Run:
        print((self.runs[run_id].model_dump() | values))
        self.runs[run_id] = Run(**(self.runs[run_id].model_dump() | values))
        print(self.runs[run_id])

        return self.runs[run_id]
