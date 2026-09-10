from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings
from backend.app.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SovAI Backend",
    description="Sovereign on-premise agentic AI workbench API",
    version=settings.SOVAI_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.SOVAI_BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "name": "SovAI Sovereign Agentic Workbench",
        "version": settings.SOVAI_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health"
    }
