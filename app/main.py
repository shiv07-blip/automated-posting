from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import PostingRequest
from app.services.posting_service import post_to_all

app = FastAPI(title="Multi-Platform Posting API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"][1:]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"success": False, "errors": errors})


@app.post("/posting")
def posting(payload: PostingRequest):
    return post_to_all(payload.message)
