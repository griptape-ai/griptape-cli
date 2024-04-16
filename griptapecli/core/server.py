from __future__ import annotations

import logging
import os
import subprocess

from dotenv import dotenv_values
from fastapi import FastAPI

from .models import Event, Run, Structure
from .state import State, RunProcess

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


state = State()


@app.post("/api/structures")
def create_structure(structure: Structure) -> Structure:
    logger.info(f"Creating structure: {structure}")
    state.register_structure(structure)

    build_structure(structure.structure_id)

    return structure


@app.get("/api/structures")
def list_structures() -> list[Structure]:
    logger.info("Listing structures")

    return list(state.structures.values())


@app.delete("/api/structures/{structure_id}")
def delete_structure(structure_id: str) -> str:
    logger.info(f"Deleting structure: {structure_id}")

    return state.remove_structure(structure_id)


@app.post("/api/structures/{structure_id}/build")
def build_structure(structure_id: str) -> Structure:
    logger.info(f"Building structure: {structure_id}")
    structure = state.get_structure(structure_id)

    structure.env = dotenv_values(f"{structure.directory}/.env")

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
def create_structure_run(structure_id: str, run: Run) -> Run:
    logger.info(f"Creating run for structure: {structure_id}")
    structure = state.get_structure(structure_id)

    process = subprocess.Popen(
        [".venv/bin/python", structure.main_file, *run.args],
        cwd=structure.directory,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env={
            **os.environ,
            **structure.env,
            **run.env,
            "GT_CLOUD_RUN_ID": run.run_id,
        },
    )
    state.runs[run.run_id] = RunProcess(run=run, process=process)

    return run


@app.get("/api/structures/{structure_id}/runs")
def list_structure_runs(structure_id: str) -> list[Run]:
    logger.info(f"Listing runs for structure: {structure_id}")
    return [
        run.run
        for run in state.runs.values()
        if run.run.structure.structure_id == structure_id
    ]


@app.patch("/api/runs/{run_id}")
def patch_run(run_id: str, values: dict) -> Run:
    logger.info(f"Patching run: {run_id}")
    cur_run = state.runs[run_id].run.model_dump()
    new_run = Run(**(cur_run | values))
    state.runs[run_id].run = new_run

    return new_run


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Run:
    logger.info(f"Getting run: {run_id}")

    run = state.runs[run_id]

    if run.process is not None:
        stdout, stderr = run.process.communicate()
        if run.process.returncode != 0:
            run.run.status = Run.Status.FAILED

        run.run.stdout = stdout
        run.run.stderr = stderr

    return state.runs[run_id].run


@app.post("/api/runs/{run_id}/events")
def create_run_event(run_id: str, event_value: dict) -> Event:
    logger.info(f"Creating event for run: {run_id}")
    event = Event(value=event_value)
    current_run = state.runs[run_id]
    current_run.run.events.append(event)

    if event.value.get("type") == "FinishStructureRunEvent":
        current_run.run.output = event.value.get("output_task_output")
        current_run.run.status = Run.Status.COMPLETED

    return event


@app.get("/api/runs/{run_id}/events")
def get_run_events(run_id: str) -> list[Event]:
    logger.info(f"Getting events for run: {run_id}")
    return state.runs[run_id].run.events
