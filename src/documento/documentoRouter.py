from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.documento.documentoService import get_documento_by_id

router = APIRouter()

@router.get("/documento/{documento_id}")
def get_documento(documento_id: int, db: Session = Depends(get_db)):
    return get_documento_by_id(db, documento_id)
