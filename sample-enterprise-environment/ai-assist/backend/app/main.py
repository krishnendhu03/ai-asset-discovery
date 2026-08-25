from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.assist import router as assist_router


app = FastAPI(
    title="AI Assist",
    description="Enterprise AI Assist with local ML and deterministic fallback.",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Health
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "ai-assist"
    }


# =========================================================
# AI Assist
# =========================================================

app.include_router(
    assist_router
)