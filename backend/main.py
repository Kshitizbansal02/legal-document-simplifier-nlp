from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from services.model_registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    await registry.load()
    yield
    registry.clear()


app = FastAPI(
    title="Legal Analyzer API",
    version="2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "models_loaded": registry.is_ready,
    }