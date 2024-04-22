from __future__ import annotations

import logging
import os
import subprocess

import psutil
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException

from .models import Event, Run, Structure
from .state import State, Run


app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


state = State()


@app.post("/api/structures")
def create_structure(structure: Structure) -> Structure:
    logger.info(f"Creating structure: {structure}")

    state.register_structure(structure)
    try:
        build_structure(structure.structure_id)
    except HTTPException as e:
        state.remove_structure(structure.structure_id)

        raise HTTPException(status_code=400, detail=str(e))

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

    _validate_files(structure)
    structure.env = dotenv_values(f"{structure.directory}/.env")
    state.register_structure(structure)

    subprocess.call(
        ["python3", "-m", "venv", ".venv"],
        cwd=structure.directory,
    )
    subprocess.call(
        [".venv/bin/pip3", "install", "-r", "requirements.txt"],
        cwd=structure.directory,
    )

    return structure


@app.post("/api/structures/{structure_id}/runs")
def create_structure_run(structure_id: str, run: Run) -> Run:
    logger.info(f"Creating run for structure: {structure_id}")
    structure = state.get_structure(structure_id)

    _validate_files(structure)

    with open("stdout", "w") as stdout, open("stderr", "w") as stderr:
        process = subprocess.Popen(
            [".venv/bin/python3", structure.main_file, *run.args],
            cwd=structure.directory,
            stdout=stdout,
            stderr=stderr,
            env={
                **os.environ,
                **structure.env,
                **run.env,
                "GT_CLOUD_RUN_ID": run.run_id,
            },
        )
        run.structure_id = structure_id
        run.process_id = process.pid
        state.runs[run.run_id] = run

        # Check if the process will fail immediately (e.g. syntax error)
        return_code = None
        try:
            return_code = psutil.Process(process.pid).wait(timeout=1)
        except psutil.TimeoutExpired:
            pass
        finally:
            if return_code != 0:
                state.runs[run.run_id].status = Run.Status.FAILED

                with open("stderr", "rb") as stderr:
                    state.update_run(
                        run.run_id,
                        {"status": Run.Status.FAILED, "stderr": stderr.read()},
                    )
                    raise HTTPException(
                        status_code=400, detail=str(state.runs[run.run_id].stderr)
                    )

    return run


@app.get("/api/structures/{structure_id}/runs")
def list_structure_runs(structure_id: str) -> list[Run]:
    logger.info(f"Listing runs for structure: {structure_id}")
    return [run for run in state.runs.values() if run.structure_id == structure_id]


@app.patch("/api/structure-runs/{run_id}")
def patch_run(run_id: str, values: dict) -> Run:
    logger.info(f"Patching run: {run_id}")
    cur_run = state.runs[run_id].model_dump()
    new_run = Run(**(cur_run | values))
    state.runs[run_id].run = new_run

    return new_run


@app.get("/api/structure-runs/{run_id}")
def get_run(run_id: str) -> Run:
    logger.info(f"Getting run: {run_id}")

    return state.runs[run_id]


@app.post("/api/structure-runs/{run_id}/events")
def create_run_event(run_id: str, event_value: dict) -> Event:
    logger.info(f"Creating event for run: {run_id}")
    event = Event(value=event_value)
    run = state.runs[run_id]
    run.events.append(event)

    if event.value.get("type") == "FinishStructureRunEvent":
        run.output = event.value.get("output_task_output")
        run.status = Run.Status.COMPLETED

    state.runs[run_id] = run

    return event


@app.get("/api/structure-runs/{run_id}/events")
def get_run_events(run_id: str) -> list[Event]:
    logger.info(f"Getting events for run: {run_id}")
    return state.runs[run_id].events


def _validate_files(structure: Structure):
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
