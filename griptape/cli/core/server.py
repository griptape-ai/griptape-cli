from __future__ import annotations
import os
from enum import Enum
from attrs import define, field, Factory
from fastapi import FastAPI
import subprocess
from typing import Optional
import uuid
from pydantic import BaseModel, Field
from dotenv import dotenv_values


app = FastAPI()


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    value: dict = Field()


class Run(BaseModel):
    class Status(Enum):
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    structure: Structure = Field(default=None)
    status: Status = Field(default=Status.RUNNING)
    events: list[Event] = Field(default_factory=lambda: [])
    output: Optional[dict] = Field(default=None)


class Structure(BaseModel):
    structure_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    directory: str = Field()
    entry_file: str = Field()
    environment: dict = Field(default_factory=lambda: {})


@define
class State:
    _active_structure: Optional[Structure] = field(default=None)
    structures: dict[str, Structure] = field(default=Factory(dict))
    runs: dict[str, Run] = field(default=Factory(dict))

    @property
    def active_structure(self) -> Structure:
        if self._active_structure is None:
            raise Exception("Structure not registered")
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


state = State()


@app.post("/api/structures")
def create_structure(structure: Structure) -> Structure:
    state.register_structure(structure)

    build_structure(structure.structure_id)

    return structure


@app.post("/api/structures/{structure_id}/build")
def build_structure(structure_id: str) -> Structure:
    structure = state.get_structure(structure_id)

    structure.environment = dotenv_values(f"{structure.directory}/.env")

    subprocess.call(
        ["python", "-m", "venv", ".venv"],
        cwd=structure.directory,
    )
    subprocess.call(
        [".venv/bin/pip", "install", "-r", "requirements.txt"],
        cwd=structure.directory,
    )

    return structure


@app.post("/api/structures/{structure_id}/runs")
def create_structure_run(structure_id: str) -> Run:
    structure = state.get_structure(structure_id)

    new_run = Run()
    state.runs[new_run.run_id] = new_run

    subprocess.Popen(
        [".venv/bin/python", structure.entry_file],
        cwd=structure.directory,
        env={**os.environ, **structure.environment, "GT_CLOUD_RUN_ID": new_run.run_id},
    )

    return new_run


@app.get("/api/structures/{structure_id}/runs")
def list_structure_runs(structure_id: str) -> list[Run]:
    return [
        run for run in state.runs.values() if run.structure.structure_id == structure_id
    ]


@app.patch("/api/runs/{run_id}")
def patch_run(run_id: str, values: dict) -> Run:
    cur_run = state.runs[run_id].model_dump()
    new_run = Run(**(cur_run | values))
    state.runs[run_id] = new_run

    return new_run


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Run:
    return state.runs[run_id]


@app.post("/api/runs/{run_id}/events")
def create_run_event(run_id: str, event_value: dict) -> Event:
    event = Event(value=event_value)
    current_run = state.runs[run_id]
    current_run.events.append(event)

    if event.value.get("type") == "FinishStructureRunEvent":
        current_run.status = Run.Status.COMPLETED
        last_task_event = next(
            (
                e
                for e in reversed(current_run.events)
                if e.value.get("type") == "FinishTaskEvent"
            ),
            None,
        )
        if last_task_event is not None:
            current_run.output = last_task_event.value.get("task_output")

    return event


@app.get("/api/runs/{run_id}/events")
def get_run_events(run_id: str) -> list[Event]:
    return state.runs[run_id].events
