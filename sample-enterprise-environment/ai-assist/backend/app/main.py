from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.assist import router as assist_router


app = FastAPI(
    title="AI Assist",
    version="1.0.0",
    description="AI-powered support assistance service",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ai-assist",
    }


app.include_router(assist_router)