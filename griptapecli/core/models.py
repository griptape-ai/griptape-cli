from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    value: dict = Field()


class StructureRun(BaseModel):
    class Status(Enum):
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    run_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    structure: Structure = Field(default=None)
    status: Status = Field(default=Status.RUNNING)
    args: list[str] = Field(default_factory=lambda: [])
    env: dict = Field(default_factory=lambda: {})
    events: list[Event] = Field(default_factory=lambda: [])
    output: Optional[dict] = Field(default=None)
    stdout: Optional[bytes] = Field(default=None)
    stderr: Optional[bytes] = Field(default=None)


class Structure(BaseModel):
    directory: str = Field()
    main_file: str = Field()
    env: dict = Field(default_factory=lambda: {})

    @computed_field
    @property
    def structure_id(self) -> str:
        path = f"{self.directory}/{self.main_file}"

        return uuid.uuid5(uuid.NAMESPACE_URL, path).hex


class ListStructuresResponseModel(BaseModel):
    structures: list[Structure] = Field(default_factory=lambda: [])


class ListStructureRunsResponseModel(BaseModel):
    structure_runs: list[StructureRun] = Field(default_factory=lambda: [])


class ListStructureRunEventsResponseModel(BaseModel):
    events: list[Event] = Field(default_factory=lambda: [])
