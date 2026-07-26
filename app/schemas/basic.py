from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    agent_id: str
    call_sid: str
    from_number: str
    to_number: str | None = None