from __future__ import annotations

import os
import datetime
import logging
import subprocess
import threading
import time
import boto3

from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from griptape.common import Message, PromptStack
from griptape.drivers import (
    AmazonBedrockCohereEmbeddingDriver,
    AmazonBedrockPromptDriver,
    AmazonBedrockTitanEmbeddingDriver,
    AzureOpenAiChatPromptDriver,
    BaseEmbeddingDriver,
    BasePromptDriver,
    GoogleEmbeddingDriver,
    GooglePromptDriver,
    AzureOpenAiEmbeddingDriver,
)

from .models import (
    Event,
    ListStructureRunEventsResponseModel,
    ListStructureRunsResponseModel,
    ListStructuresResponseModel,
    ListStructureRunLogsResponseModel,
    Structure,
    StructureRun,
    Log,
    PromptDriverRequestModel,
    EmbeddingDriverRequestModel,
)
from .state import RunProcess, State

from routellm.controller import Controller

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


state = State()

controller = Controller(
    routers=["mf"],
    strong_model="gpt-4o",
    weak_model="llama3-8b-instruct",
)

DEFAULT_QUEUE_DELAY = "2"

model_to_internal_model_map: dict[str, str] = {
    # Azure OpenAi
    "gpt-4o": "gpt-4o",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "text-embedding-3-large": "text-embedding-3-large",
    "text-embedding-3-small": "text-embedding-3-small",
    # Bedrock
    "titan-embed-text": "amazon.titan-embed-text-v1",
    "embed-english": "cohere.embed-english-v3",
    "claude-3-sonnet-20240229": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3-haiku-20240307": "anthropic.claude-3-haiku-20240307-v1:0",
    "j2-ultra": "ai21.j2-ultra",
    "j2-mid": "ai21.j2-mid",
    "titan-text-lite": "amazon.titan-text-lite-v1",
    "command-r-plus": "cohere.command-r-plus-v1:0",
    "command-r": "cohere.command-r-v1:0",
    "command-text": "cohere.command-text-v14",
    "command-light-text": "cohere.command-light-text-v14",
    "llama3-8b-instruct": "meta.llama3-8b-instruct-v1:0",
    "llama3-70b-instruct": "meta.llama3-70b-instruct-v1:0",
    "llama2-13b-chat": "meta.llama2-13b-chat-v1",
    "llama2-70b-chat": "meta.llama2-70b-chat-v1",
    "mistral-7b-instruct": "mistral.mistral-7b-instruct-v0:2",
    "mixtral-8x7b-instruct": "mistral.mixtral-8x7b-instruct-v0:1",
    "mistral-large-2402": "mistral.mistral-large-2402-v1:0",
    "mistral-small-2402": "mistral.mistral-small-2402-v1:0",
    # Gemini
    "gemini-1.0-pro": "gemini-1.0-pro",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
}

model_prefix_to_prompt_driver_map: dict[str, type[BasePromptDriver]] = {
    "gpt": AzureOpenAiChatPromptDriver,
    "anthropic": AmazonBedrockPromptDriver,
    "ai21": AmazonBedrockPromptDriver,
    "amazon": AmazonBedrockPromptDriver,
    "meta": AmazonBedrockPromptDriver,
    "mistral": AmazonBedrockPromptDriver,
    "gemini": GooglePromptDriver,
}

model_prefix_to_embedding_driver_map: dict[str, type[BaseEmbeddingDriver]] = {
    "text-embedding-3-small": AzureOpenAiEmbeddingDriver,
    "text-embedding-3-large": AzureOpenAiEmbeddingDriver,
    "titan-embed": AmazonBedrockTitanEmbeddingDriver,
    "embed-english": AmazonBedrockCohereEmbeddingDriver,
    "text-embedding-004": GoogleEmbeddingDriver,
}

embedding_driver_to_config_map: dict[type[BaseEmbeddingDriver], dict] = {
    AmazonBedrockTitanEmbeddingDriver: {
        "session": boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_DEFAULT_REGION"],
        ),
    },
    AzureOpenAiEmbeddingDriver: {
        "api_key": os.environ["GOOGLE_API_KEY"],
    },
    AmazonBedrockCohereEmbeddingDriver: {
        "api_key": os.environ["AZURE_OPENAI_API_KEY"],
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    },
}

prompt_driver_to_config_map: dict[type[BasePromptDriver], dict] = {
    AmazonBedrockPromptDriver: {
        "session": boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_DEFAULT_REGION"],
        ),
    },
    GooglePromptDriver: {
        "api_key": os.environ["GOOGLE_API_KEY"],
    },
    AzureOpenAiChatPromptDriver: {
        "api_key": os.environ["AZURE_OPENAI_API_KEY"],
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    },
}


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
    cur_run = state.runs[structure_run_id].run.model_dump()  # type: ignore
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
def create_run_event(
    structure_run_id: str, event_value: dict | list[dict]
) -> Event | list[Event]:
    if isinstance(event_value, dict):
        event_values = [event_value]
    else:
        event_values = event_value

    events = []
    for event_value in event_values:
        logger.info(f"Creating event for run: {structure_run_id}")
        event = Event(value=event_value)
        events.append(event)
        current_run = state.runs[structure_run_id]
        current_run.run.events.append(event)

        if event.value.get("type") == "FinishStructureRunEvent":
            current_run.run.output = event.value.get("output_task_output")
            _check_run_process(current_run)

    return events


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


@app.post("/api/drivers/prompt", response_model=None, status_code=status.HTTP_200_OK)
def prompt_driver(value: PromptDriverRequestModel) -> dict:
    driver = _get_prompt_driver_from_model(value.messages, value.params)

    prompt_stack = PromptStack(
        messages=[Message.from_dict(message) for message in value.messages]
    )

    try:
        message = driver.try_run(prompt_stack)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return message.to_dict()


@app.post(
    "/api/drivers/prompt-stream", response_model=None, status_code=status.HTTP_200_OK
)
async def prompt_driver_stream(value: PromptDriverRequestModel) -> StreamingResponse:
    driver = _get_prompt_driver_from_model(value.messages, value.params)

    prompt_stack = PromptStack(
        messages=[Message.from_dict(message) for message in value.messages]
    )

    async def chunks_streamer():
        try:
            for i in driver.try_stream(prompt_stack):
                yield i.to_json()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(chunks_streamer())


@app.post("/api/drivers/embedding", status_code=status.HTTP_200_OK)
def embedding(value: EmbeddingDriverRequestModel) -> list[float]:
    driver = _get_embedding_driver_from_model(value.params)

    embeddings = driver.embed_string(value.input)

    return embeddings


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


def _get_prompt_driver_from_model(
    messages: list[dict], params: dict
) -> BasePromptDriver:
    model = params["model"]

    if model == "auto":
        if messages:
            logger.info(messages[-1]["content"][0]["artifact"]["value"])
            prompt = messages[-1]["content"][0]["artifact"]["value"]
        else:
            raise HTTPException(status_code=400, detail="No messages provided")

        model = controller.route(
            prompt=prompt,
            router="mf",
            threshold=0.11593,
        )
        logger.info("Routed model %s", model)

    internal_model = model_to_internal_model_map.get(model)

    logger.info("Internal model %s", internal_model)
    if internal_model is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    driver_cls = next(
        (
            v
            for k, v in model_prefix_to_prompt_driver_map.items()
            if internal_model.startswith(k)
        ),
        None,
    )

    logger.info("Driver class %s", driver_cls)
    if driver_cls is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    driver_config = prompt_driver_to_config_map.get(driver_cls)

    if driver_config is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    full_params = params | {"model": internal_model} | driver_config
    logger.info(full_params)
    return driver_cls(**full_params)


def _get_embedding_driver_from_model(params: dict) -> BaseEmbeddingDriver:
    model = params["model"]
    logger.info("Model %s", model)

    internal_model = model_to_internal_model_map.get(model)

    logger.info("Internal model %s", internal_model)
    if internal_model is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    driver_cls = next(
        (
            v
            for k, v in model_prefix_to_embedding_driver_map.items()
            if internal_model.startswith(k)
        ),
        None,
    )

    logger.info("Driver class %s", driver_cls)
    if driver_cls is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    driver_config = embedding_driver_to_config_map.get(driver_cls)

    if driver_config is None:
        raise HTTPException(status_code=400, detail=f"Model {model} not supported")

    full_params = params | {"model": internal_model} | driver_config
    logger.info(full_params)
    return driver_cls(**full_params)
