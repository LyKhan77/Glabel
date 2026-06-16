from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1 import projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Future: load Ultralytics models, init WebSocket connection manager.
    yield
    # Future: cleanup.


app = FastAPI(title="Glabel Backend API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)


@app.get("/health")
def health():
    return {"status": "ok"}
