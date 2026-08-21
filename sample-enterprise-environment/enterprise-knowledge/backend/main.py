from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.knowledge import router as knowledge_router


app = FastAPI(
    title="Enterprise Knowledge",
    version="1.0.0",
    description="Enterprise support knowledge service",
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
        "service": "enterprise-knowledge",
    }


app.include_router(knowledge_router)