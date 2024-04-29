from __future__ import annotations

import datetime
import logging
import os
import subprocess
import threading
import time

from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, status, Request
from .models import (
    Event,
    ListStructureRunEventsResponseModel,
    ListStructureRunsResponseModel,
    ListStructuresResponseModel,
    ListStructureRunLogsResponseModel,
    Structure,
    StructureRun,
    Log,
)
from .state import RunProcess, State

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


state = State()

DEFAULT_QUEUE_DELAY = "2"


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
def create_structure_run(
    structure_id: str, run: StructureRun, request: Request
) -> StructureRun:
    logger.info(f"Creating run for structure: {structure_id}")
    structure = state.get_structure(structure_id)

    _validate_files(structure)

    process = subprocess.Popen(
        [".venv/bin/python3", structure.main_file, *run.args],
        cwd=structure.directory,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env={
            "GT_CLOUD_STRUCTURE_RUN_ID": run.structure_run_id,
            "GT_CLOUD_BASE_URL": str(request.base_url),
            **os.environ,
            **structure.env,
            **run.env,
        },
    )
    state.runs[run.structure_run_id] = RunProcess(run=run, process=process)

    threading.Thread(
        target=_set_structure_run_to_running,
        args=(state.runs[run.structure_run_id].run,),
    ).start()

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


@app.patch("/api/structure-runs/{structure_run_id}", status_code=status.HTTP_200_OK)
def patch_run(structure_run_id: str, values: dict) -> StructureRun:
    logger.info(f"Patching run: {structure_run_id}")
    cur_run = state.runs[structure_run_id].run.model_dump()
    new_run = StructureRun(**(cur_run | values))
    state.runs[structure_run_id].run = new_run

    return new_run


@app.get("/api/structure-runs/{structure_run_id}", status_code=status.HTTP_200_OK)
def get_run(structure_run_id: str) -> StructureRun:
    logger.info(f"Getting run: {structure_run_id}")

    run = state.runs[structure_run_id]

    _check_run_process(run)

    return state.runs[structure_run_id].run


@app.post(
    "/api/structure-runs/{structure_run_id}/events", status_code=status.HTTP_201_CREATED
)
def create_run_event(structure_run_id: str, event_value: dict) -> Event:
    logger.info(f"Creating event for run: {structure_run_id}")
    event = Event(value=event_value)
    current_run = state.runs[structure_run_id]
    current_run.run.events.append(event)

    if event.value.get("type") == "FinishStructureRunEvent":
        current_run.run.output = event.value.get("output_task_output")
        _check_run_process(current_run)

    return event


@app.get(
    "/api/structure-runs/{structure_run_id}/events",
    status_code=status.HTTP_200_OK,
    response_model=ListStructureRunEventsResponseModel,
)
def list_run_events(structure_run_id: str):
    logger.info(f"Getting events for run: {structure_run_id}")

    events = state.runs[structure_run_id].run.events

    sorted_events = sorted(events, key=lambda event: event.value["timestamp"])

    return {
        "events": sorted_events,
    }


@app.get(
    "/api/structure-runs/{structure_run_id}/logs",
    status_code=status.HTTP_200_OK,
    response_model=ListStructureRunLogsResponseModel,
)
def list_run_logs(structure_run_id: str):
    logger.info(f"Getting logs for run: {structure_run_id}")

    logs = state.runs[structure_run_id].run.logs

    return {
        "logs": logs,
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

            timestamp = datetime.datetime.now().isoformat()
            if stdout is not None and stdout != b"":
                run_process.run.logs.append(
                    Log(time=timestamp, message=stdout, stream=Log.Stream.STDOUT)
                )

            if stderr is not None and stderr != b"":
                run_process.run.logs.append(
                    Log(time=timestamp, message=stderr, stream=Log.Stream.STDERR)
                )

    return run_process


def _set_structure_run_to_running(structure_run: StructureRun) -> StructureRun:
    run_delay = int(os.getenv("GT_SKATEPARK_QUEUE_DELAY", DEFAULT_QUEUE_DELAY))

    time.sleep(run_delay)

    structure_run.status = StructureRun.Status.RUNNING

    return structure_run
