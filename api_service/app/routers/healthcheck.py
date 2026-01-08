from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.utils.response import SuccessResponse

router = APIRouter(prefix='/healthcheck', tags=['healthcheck'])


@router.get(
    '',
    summary="Check service health",
    description="Endpoint to check the health of the service.",
    responses={
        200: {
            "description": "Service is healthy.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {"status": "ok"},
                        "error": None
                    }
                }
            }
        }
    },
    status_code=status.HTTP_200_OK,
)
def healthcheck() -> JSONResponse:
    return SuccessResponse(data={"status": "ok"})
