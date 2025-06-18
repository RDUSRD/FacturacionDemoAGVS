from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.auditoria.auditoriaService import log_auditoria

router = APIRouter()

@router.post("/auditoria")
def log_auditoria_endpoint(auditoria_data: dict, db: Session = Depends(get_db)):
    return log_auditoria(db, auditoria_data)
