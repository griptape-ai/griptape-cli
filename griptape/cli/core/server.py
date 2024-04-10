from __future__ import annotations
import os
from enum import Enum
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
    status: Status = Field(default=Status.RUNNING)
    events: list[Event] = Field(default_factory=lambda: [])
    output: Optional[dict] = Field(default=None)


class Structure(BaseModel):
    structure_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    directory: str = Field()
    entry_file: str = Field()
    runs: dict[str, Run] = Field(default_factory=lambda: {})
    environment: dict = Field(default_factory=lambda: {})


structures: dict[str, Structure] = {
    "1": Structure(
        structure_id="1",
        directory="/Users/collindutter/Documents/griptape/griptape-playground/src/misc/local-emulator/",
        entry_file="structure.py",
        runs={
            "1": Run(
                run_id="1",
            )
        },
    ),
}

current_run: Optional[Run] = None


@app.post("/api/structures")
def create_structure(structure: Structure) -> Structure:
    structure_id = structure.structure_id
    structures[structure_id] = structure

    structure.environment = dotenv_values(f"{structures[structure_id].directory}/.env")

    subprocess.call(
        ["python", "-m", "venv", ".venv"],
        cwd=structures[structure_id].directory,
    )
    subprocess.call(
        [".venv/bin/pip", "install", "-r", "requirements.txt"],
        cwd=structures[structure_id].directory,
    )

    return structure


@app.get("/api/structures/{structure_id}")
def get_structures(structure_id: str) -> Structure:
    return structures[structure_id]


@app.get("/api/structures")
def list_structures() -> list[Structure]:
    return list(structures.values())


@app.post("/api/structures/{structure_id}/runs")
def create_structure_run(structure_id: str) -> Run:
    new_run = Run()
    structure = structures[structure_id]
    structure.runs[new_run.run_id] = new_run

    global current_run
    current_run = new_run
    subprocess.Popen(
        [".venv/bin/python", structure.entry_file],
        cwd=structure.directory,
        env={**os.environ, **structure.environment, "GT_CLOUD_RUN_ID": new_run.run_id},
    )

    return new_run


@app.get("/api/structures/{structure_id}/runs/{run_id}")
def get_structure_run(structure_id: str, run_id: str) -> Run:
    return structures[structure_id].runs[run_id]


@app.get("/api/structures/{structure_id}/runs")
def list_structure_runs(structure_id: str) -> list[Run]:
    return list(structures[structure_id].runs.values())


@app.patch("/api/structures/{structure_id}/runs/{run_id}")
def patch_structure_run(structure_id: str, run_id: str, values: dict) -> Run:
    cur_run = structures[structure_id].runs[run_id].model_dump()
    new_run = Run(**(cur_run | values))
    structures[structure_id].runs[run_id] = new_run

    return new_run


@app.post("/api/runs/{run_id}/events")
def create_run_event(run_id: str, event_value: dict) -> Event:
    event = Event(value=event_value)
    if current_run is None:
        raise Exception("No current run")
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
    return structures[run_id].runs[run_id].events


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Run:
    return structures[run_id].runs[run_id]
