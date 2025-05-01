from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from starlette import status

from app.core.request import ReqDep
from app.database.database import Database

router = APIRouter()


@router.get("/service", status_code=status.HTTP_200_OK)
def check_service_health():
    return {"status": "Healthy"}


@router.get("/database", status_code=status.HTTP_200_OK)
def check_database_health(db: Database = ReqDep(Database)):
    try:
        with db.resolve_session() as session:
            session.execute(text("SELECT 1"))
            return {"status": "Healthy"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
