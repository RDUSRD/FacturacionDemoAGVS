from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.empresa.empresaService import get_or_create_empresa

router = APIRouter()

@router.post("/empresa")
def create_or_get_empresa(empresa_data: dict, db: Session = Depends(get_db)):
    return get_or_create_empresa(db, empresa_data)
