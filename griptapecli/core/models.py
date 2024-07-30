from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

STRUCTURE_CONFIG_RUNTIME__PYTHON_3 = "python3"
STRUCTURE_CONFIG_RUNTIME_VERSION__PYTHON_3_11 = "3.11"

STRUCTURE_CONFIG_VERSION = "1.0"
STRUCTURE_CONFIG_RUNTIME = STRUCTURE_CONFIG_RUNTIME__PYTHON_3
STRUCTURE_CONFIG_RUNTIME_VERSION = STRUCTURE_CONFIG_RUNTIME_VERSION__PYTHON_3_11


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    value: dict = Field()


class Log(BaseModel):
    class Stream(Enum):
        STDOUT = "stdout"
        STDERR = "stderr"

    time: str = Field()
    message: str = Field()
    stream: Stream = Field()


class CacheBuildDependenciesField(BaseModel):
    enabled: bool = False
    watched_files: list[str] = Field(default_factory=list)


class StructureConfigBuildField(BaseModel):
    pre_build_install_script: Optional[str] = None
    post_build_install_script: Optional[str] = None
    requirements_file: Optional[str] = None
    cache_build_dependencies: CacheBuildDependenciesField = Field(
        default_factory=lambda: CacheBuildDependenciesField()
    )


class StructureConfigRunField(BaseModel):
    main_file: str


class StructureConfig(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    version: str
    runtime: str
    runtime_version: str
    build: StructureConfigBuildField = Field(
        default_factory=lambda: StructureConfigBuildField()
    )
    run: StructureConfigRunField

    @field_validator("version")
    @classmethod
    def validate_version_field(cls, version_field: str):
        if not version_field == STRUCTURE_CONFIG_VERSION:
            raise ValueError(f"Unsupported version {version_field}")
        return version_field

    @field_validator("runtime")
    @classmethod
    def validate_runtime_field(cls, runtime_field: str):
        if not runtime_field == STRUCTURE_CONFIG_RUNTIME:
            raise ValueError(f"Unsupported runtime {runtime_field}")
        return runtime_field

    @field_validator("runtime_version")
    @classmethod
    def validate_runtime_version_field(cls, runtime_version_field: str):
        if not runtime_version_field == STRUCTURE_CONFIG_RUNTIME_VERSION:
            raise ValueError(f"Unsupported runtime version {runtime_version_field}")
        return runtime_version_field

    def to_json_str_representation(self) -> str:
        return self.model_dump_json()

    def __str__(self):
        return self.to_json_str_representation()


class StructureRunInput(BaseModel):
    args: list[str] = Field(default_factory=lambda: [])
    env: dict = Field(default_factory=lambda: {})


class StructureRun(BaseModel):
    class Status(Enum):
        RUNNING = "RUNNING"
        SUCCEEDED = "SUCCEEDED"
        QUEUED = "QUEUED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

    structure_run_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    structure: Structure = Field(default=None)
    status: Status = Field(default=Status.QUEUED)
    args: list[str] = Field(default_factory=lambda: [])
    env: dict = Field(default_factory=lambda: {})
    events: list[Event] = Field(default_factory=lambda: [])
    logs: list[Log] = Field(default_factory=lambda: [])
    output: Optional[dict] = Field(default=None)


class Structure(BaseModel):
    directory: str = Field()
    structure_config_file: str = Field()
    env: dict = Field(default_factory=lambda: {})

    @computed_field
    @property
    def structure_id(self) -> str:
        path = f"{self.directory}/{self.structure_config_file}"

        return uuid.uuid5(uuid.NAMESPACE_URL, path).hex

    @computed_field
    @property
    def structure_config(self) -> StructureConfig:
        config_path = f"{self.directory}/{self.structure_config_file}"
        with open(config_path, "r") as config_file:
            return StructureConfig(**yaml.safe_load(config_file))


class ListStructuresResponseModel(BaseModel):
    structures: list[Structure] = Field(default_factory=lambda: [])


class ListStructureRunsResponseModel(BaseModel):
    structure_runs: list[StructureRun] = Field(default_factory=lambda: [])


class ListStructureRunEventsResponseModel(BaseModel):
    events: list[Event] = Field(default_factory=lambda: [])


class ListStructureRunLogsResponseModel(BaseModel):
    logs: list[Log] = Field(default_factory=lambda: [])
