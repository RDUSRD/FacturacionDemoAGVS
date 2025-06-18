from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.notas.notaService import create_nota_debito, create_nota_credito

router = APIRouter()

@router.post("/nota_debito")
def create_nota_debito_endpoint(nota_debito_data: dict, db: Session = Depends(get_db)):
    return create_nota_debito(db, nota_debito_data)

@router.post("/nota_credito")
def create_nota_credito_endpoint(nota_credito_data: dict, db: Session = Depends(get_db)):
    return create_nota_credito(db, nota_credito_data)
