from fastapi import FastAPI
from typing import Union

app = FastAPI()

structures = []


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/api/structures/{structure_id}/runs")
def create_run(structure_id: str, run_args: dict) -> dict:
    return {
        "structure_id": structure_id,
        "run_args": run_args,
    }


@app.get("/api/structures/{structure_id}/runs")
def list_runs(structure_id: str) -> list:
    # returns list of all runs of the program
    return []


@app.get("/api/structures/{structure_id}/runs/{run_id}")
def get_run(structure_id: str, run_id: str) -> dict:
    # get the run and return the object
    return {}


@app.put("/api/structures/{structure_id}/runs/{run_id}/cancel")
def cancel_run(run_id: str) -> None:
    return None
