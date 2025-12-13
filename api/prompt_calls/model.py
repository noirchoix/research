# -------------------------------------------------------------------
# Pydantic models for request/response
# -------------------------------------------------------------------
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

class TagIn(BaseModel):
    name: str
    value: str


class PromptBuilderRequest(BaseModel):
    tags: List[TagIn]
    pattern_names: List[str]


class PromptBuilderResponse(BaseModel):
    prompt_text: str
    score: float
    accepted: bool
    download_url: Optional[str]


@dataclass
class PromptResult:
    prompt_text: str
    score: float
    accepted: bool
    file_path: str | None

