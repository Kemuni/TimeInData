from typing import TypeVar, Optional, Any
from fastapi import status
from fastapi.responses import JSONResponse

from app.schemas import APIResponse, ErrorDetail

T = TypeVar('T')


class SuccessResponse(JSONResponse):
    """ Standardized success response class """
    
    def __init__(
        self,
        data: Optional[Any] = None,
        status_code: int = status.HTTP_200_OK,
        **kwargs
    ):
        response = APIResponse(
            success=True,
            data=data,
            error=None
        )
        super().__init__(
            content=response.model_dump(mode='json', exclude_none=False),
            status_code=status_code,
            **kwargs
        )


class ErrorResponse(JSONResponse):
    """ Standardized error response class """
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        **kwargs
    ):
        response = APIResponse(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message)
        )
        super().__init__(
            content=response.model_dump(mode='json', exclude_none=False),
            status_code=status_code,
            **kwargs
        )
