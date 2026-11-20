import re
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, field_validator

URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:!?)]}"
HttpUrlAdapter = TypeAdapter(HttpUrl)


class PostingRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=200)]

    @field_validator("message")
    @classmethod
    def validate_single_cta_link(cls, value: str) -> str:
        links = [raw.rstrip(TRAILING_PUNCTUATION) for raw in URL_PATTERN.findall(value)]
        if len(links) != 1:
            raise ValueError(
                f"message must contain exactly one CTA link; found {len(links)}"
            )
        try:
            HttpUrlAdapter.validate_python(links[0])
        except ValueError as exc:
            raise ValueError(f"invalid CTA link: {links[0]}") from exc
        return value


class PlatformResult(BaseModel):
    platform: str
    status: str
    posted_url: str | None = None
    public_access: bool = False
    date: str | None = None
    time: str | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
