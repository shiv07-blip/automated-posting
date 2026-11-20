from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import httpx

from app.platforms import build_platforms
from app.platforms.base import BasePlatform
from app.schemas import PlatformResult, PostingResponse

USER_AGENT = "ChivoxPracticalTest/1.0 (github.com/chivoxai/practical-test)"


def post_one(platform: BasePlatform, message: str, client: httpx.Client) -> PlatformResult:
    now = datetime.now(timezone.utc)
    try:
        url = platform.post(message, client)
    except Exception as exc:  # noqa: BLE001 - one platform must never stop the others
        return PlatformResult(
            platform=platform.name,
            status="failed",
            error=f"{type(exc).__name__}: {str(exc)[:300]}",
        )
    return PlatformResult(
        platform=platform.name,
        status="success",
        posted_url=url,
        public_access=True,
        date=now.date().isoformat(),
        time=now.time().replace(microsecond=0).isoformat(),
    )


def post_to_all(message: str) -> PostingResponse:
    platforms = build_platforms()
    with httpx.Client(
        headers={"User-Agent": USER_AGENT}, timeout=20, follow_redirects=True
    ) as client, ThreadPoolExecutor(max_workers=len(platforms)) as pool:
        futures = [pool.submit(post_one, p, message, client) for p in platforms]
        results = [future.result() for future in futures]
    return PostingResponse(
        success=any(result.status == "success" for result in results), results=results
    )
