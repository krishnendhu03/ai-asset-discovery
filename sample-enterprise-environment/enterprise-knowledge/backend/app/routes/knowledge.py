from fastapi import APIRouter

from app.models.knowledge import (
    KnowledgeRequest,
    KnowledgeResponse,
)

from app.services.knowledge_service import search_knowledge


router = APIRouter(
    prefix="/knowledge",
    tags=["Enterprise Knowledge"],
)


@router.post(
    "/",
    response_model=KnowledgeResponse,
)
def knowledge(request: KnowledgeRequest):
    return search_knowledge(request)