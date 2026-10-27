from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .advisor import advise
from .classifier import classify

app = FastAPI(title="ScamShield Bharat", version="0.1.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class CheckRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)
    lang: str = "en"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/check")
def check(req: CheckRequest):
    result = classify(req.message)
    return {**result, **advise(result, req.lang), "lang": req.lang}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")
