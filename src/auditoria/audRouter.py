from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.auditoria.audService import log_auditoria

router = APIRouter(tags=["Auditoria"], prefix="/auditoria")

@router.post("/log", response_model=dict)
def log_auditoria_endpoint(auditoria_data: dict, db: Session = Depends(get_db)):
    return log_auditoria(db, auditoria_data)
