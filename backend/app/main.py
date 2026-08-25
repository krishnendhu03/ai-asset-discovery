from fastapi import FastAPI

from app.routes.discovery import router as discovery_router
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models.database import AssetRecord


Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="AI Asset Discovery",
    description="Enterprise AI asset discovery and inventory service",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ai-asset-discovery",
    }


app.include_router(discovery_router)