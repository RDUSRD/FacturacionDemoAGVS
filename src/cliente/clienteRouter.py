from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.cliente.clienteService import get_or_create_cliente

router = APIRouter()

@router.post("/cliente")
def create_or_get_cliente(cliente_data: dict, db: Session = Depends(get_db)):
    return get_or_create_cliente(db, cliente_data)
