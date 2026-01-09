from fastapi import HTTPException


def bad_request(description: str):
    raise HTTPException(
        status_code=400,
        detail={
            "error": {
                "code": "BAD_REQUEST_ERROR",
                "description": description,
            }
        },
    )


def not_found(description: str):
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND_ERROR",
                "description": description,
            }
        },
    )


def authentication_error(description: str):
    raise HTTPException(
        status_code=401,
        detail={
            "error": {
                "code": "AUTHENTICATION_ERROR",
                "description": description,
            }
        },
    )


def internal_error(description: str = "Something went wrong"):
    raise HTTPException(
        status_code=500,
        detail={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "description": description,
            }
        },
    )