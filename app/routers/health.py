from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:

    return {"status": "ok"}
