from enum import Enum
from pydantic import BaseModel, field_validator


class Priority(str, Enum):
    HIGH = "High"
    MED = "Med"
    LOW = "Low"


class Assignee(str, Enum):
    DEV = "Dev"
    CLIENT = "Client"
    UNASSIGNED = "Unassigned"


class ActionItem(BaseModel):
    title: str
    priority: Priority
    assignee: Assignee
    details: str

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v):
        if isinstance(v, str):
            v_title = v.capitalize()
            if v_title in ["High", "Med", "Low"]:
                return Priority(v_title)
            # Default fallback for minor formatting variations
            if "high" in v.lower():
                return Priority.HIGH
            if "low" in v.lower():
                return Priority.LOW
            return Priority.MED
        return v

    @field_validator("assignee", mode="before")
    @classmethod
    def normalize_assignee(cls, v):
        if isinstance(v, str):
            v_title = v.capitalize()
            if v_title in ["Dev", "Client", "Unassigned"]:
                return Assignee(v_title)
            if "client" in v.lower():
                return Assignee.CLIENT
            if "dev" in v.lower() or "engineer" in v.lower():
                return Assignee.DEV
            return Assignee.UNASSIGNED
        return v


class ExtractionResult(BaseModel):
    summary: str
    action_items: list[ActionItem]
    client_email: str

