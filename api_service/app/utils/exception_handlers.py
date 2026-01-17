from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app.schemas import APIResponse, ErrorDetail


async def pydantic_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """ Handle Pydantic validation errors with human-readable messages. """
    errors = exc.errors()

    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        msg = error.get("msg", "Validation error")
        error_type = error.get("type", "")
        
        # Make error messages more user-friendly
        if "missing" in error_type:
            readable_msg = f"Field '{field}' is required but missing"
        elif "type_error" in error_type or "int_parsing" in error_type or "float_parsing" in error_type:
            readable_msg = f"Field '{field}' has invalid type: {msg}"
        elif "greater_than" in error_type:
            readable_msg = f"Field '{field}' must be greater than specified value"
        elif "less_than" in error_type:
            readable_msg = f"Field '{field}' must be less than specified value"
        elif "string_too_short" in error_type or "string_too_long" in error_type:
            readable_msg = f"Field '{field}' length is invalid: {msg}"
        else:
            readable_msg = f"Field '{field}': {msg}" if field else msg
        
        error_messages.append(readable_msg)
    
    # Combine all errors into a single message
    combined_message = "; ".join(error_messages)

    logger.warning(f"Validation error on {request.url.path}: {combined_message}")

    response = APIResponse(
        success=False,
        data=None,
        error=ErrorDetail(
            code="VALIDATION_ERROR",
            message=combined_message
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """ Handle all unhandled exceptions with standard format. """
    # If the exception is HTTPException, return it as is
    if isinstance(exc, HTTPException):
        response = APIResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code=str(exc.status_code),
                message=exc.detail
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump()
        )

    # Log all other unhandled exceptions
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    response = APIResponse(
        success=False,
        data=None,
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message="An internal server error occurred. Please try again later."
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump()
    )
