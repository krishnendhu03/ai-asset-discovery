from fastapi import APIRouter

from app.models.assist import (
    AssistRequest,
    AssistResponse
)

from app.services.ai_assist import (
    generate_assistance
)


router = APIRouter(
    prefix="/assist",
    tags=["AI Assist"]
)


@router.post(
    "/",
    response_model=AssistResponse
)
def assist(
    request: AssistRequest
):

    return generate_assistance(request)