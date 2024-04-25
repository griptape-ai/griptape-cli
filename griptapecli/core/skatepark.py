from __future__ import annotations

import logging
import os
import subprocess

from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, status
from .models import (
    Event,
    StructureRun,
    Structure,
    ListStructuresResponseModel,
    ListStructureRunsResponseModel,
    ListStructureRunEventsResponseModel,
)
from .state import State, RunProcess

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


state = State()


@app.post("/api/structures", status_code=status.HTTP_201_CREATED)
def create_structure(structure: Structure) -> Structure:
    logger.info(f"Creating structure: {structure}")

    state.register_structure(structure)
    try:
        build_structure(structure.structure_id)
    except HTTPException as e:
        state.remove_structure(structure.structure_id)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return structure


@app.get(
    "/api/structures",
    response_model=ListStructuresResponseModel,
    status_code=status.HTTP_200_OK,
)
def list_structures():
    logger.info("Listing structures")

    return {"structures": list(state.structures.values())}


@app.delete("/api/structures/{structure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_structure(structure_id: str):
    logger.info(f"Deleting structure: {structure_id}")

    state.remove_structure(structure_id)


@app.post("/api/structures/{structure_id}/build", status_code=status.HTTP_201_CREATED)
def build_structure(structure_id: str) -> Structure:
    logger.info(f"Building structure: {structure_id}")
    structure = state.get_structure(structure_id)

    _validate_files(structure)
    structure.env = dotenv_values(f"{structure.directory}/.env")

    subprocess.call(
        ["python3", "-m", "venv", ".venv"],
        cwd=structure.directory,
    )
    subprocess.call(
        [".venv/bin/pip3", "install", "-r", "requirements.txt"],
        cwd=structure.directory,
    )

    return structure


@app.post("/api/structures/{structure_id}/runs", status_code=status.HTTP_201_CREATED)
def create_structure_run(structure_id: str, run: StructureRun) -> StructureRun:
    logger.info(f"Creating run for structure: {structure_id}")
    structure = state.get_structure(structure_id)

    _validate_files(structure)

    process = subprocess.Popen(
        [".venv/bin/python3", structure.main_file, *run.args],
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


@app.get(
    "/api/structures/{structure_id}/runs",
    response_model=ListStructureRunsResponseModel,
    status_code=status.HTTP_200_OK,
)
def list_structure_runs(structure_id: str):
    logger.info(f"Listing runs for structure: {structure_id}")

    return {
        "structure_runs": [
            run.run
            for run in state.runs.values()
            if run.run.structure.structure_id == structure_id
        ]
    }


@app.patch("/api/structure-runs/{run_id}", status_code=status.HTTP_200_OK)
def patch_run(run_id: str, values: dict) -> StructureRun:
    logger.info(f"Patching run: {run_id}")
    cur_run = state.runs[run_id].run.model_dump()
    new_run = StructureRun(**(cur_run | values))
    state.runs[run_id].run = new_run

    return new_run


@app.get("/api/structure-runs/{run_id}", status_code=status.HTTP_200_OK)
def get_run(run_id: str) -> StructureRun:
    logger.info(f"Getting run: {run_id}")

    run = state.runs[run_id]

    _check_run_process(run)

    return state.runs[run_id].run


@app.post("/api/structure-runs/{run_id}/events", status_code=status.HTTP_201_CREATED)
def create_run_event(run_id: str, event_value: dict) -> Event:
    logger.info(f"Creating event for run: {run_id}")
    event = Event(value=event_value)
    current_run = state.runs[run_id]
    current_run.run.events.append(event)

    if event.value.get("type") == "FinishStructureRunEvent":
        current_run.run.output = event.value.get("output_task_output")
        _check_run_process(current_run)

    return event


@app.get(
    "/api/structure-runs/{run_id}/events",
    status_code=status.HTTP_200_OK,
    response_model=ListStructureRunEventsResponseModel,
)
def list_run_events(run_id: str):
    logger.info(f"Getting events for run: {run_id}")

    events = state.runs[run_id].run.events

    sorted_events = sorted(events, key=lambda event: event.value["timestamp"])

    return {
        "events": sorted_events,
    }


def _validate_files(structure: Structure) -> None:
    if not os.path.exists(structure.directory):
        raise HTTPException(status_code=400, detail="Directory does not exist")

    if not os.path.isdir(structure.directory):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    if not os.path.exists(f"{structure.directory}/{structure.main_file}"):
        raise HTTPException(status_code=400, detail="Main file does not exist")

    if not os.path.isfile(f"{structure.directory}/{structure.main_file}"):
        raise HTTPException(status_code=400, detail="Main file is not a file")

    if not os.path.exists(f"{structure.directory}/requirements.txt"):
        raise HTTPException(status_code=400, detail="requirements.txt does not exist")


def _check_run_process(run_process: RunProcess) -> RunProcess:
    process = run_process.process

    if process is not None:
        return_code = process.poll()
        if return_code is not None:
            stdout, stderr = run_process.process.communicate()
            if return_code == 0:
                run_process.run.status = StructureRun.Status.SUCCEEDED
            else:
                run_process.run.status = StructureRun.Status.FAILED

            run_process.run.stdout = stdout
            run_process.run.stderr = stderr

    return run_process
