from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

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
                    "example": {"status": "ok"}
                }
            }
        },
        400: {
            "description": "Service health check failed.",
            "content": {
                "application/json": {
                    "example": {"status": "bad request"}
                }
            }
        },
    },
    status_code=status.HTTP_200_OK,
)
def healthcheck() -> JSONResponse:
    return JSONResponse({'status': 'ok'})
