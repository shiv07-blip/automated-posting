from abc import ABC, abstractmethod

import httpx


class BasePlatform(ABC):
    name: str

    @abstractmethod
    def post(self, message: str, client: httpx.Client) -> str:
        """Publish the message and return the URL of the public post."""

    @staticmethod
    def check(response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"HTTP {response.status_code}: {response.text[:200]}"
            ) from exc
