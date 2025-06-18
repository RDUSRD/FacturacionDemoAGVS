from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.orden_entrega.ordenEntregaService import create_orden_entrega

router = APIRouter()

@router.post("/orden_entrega")
def create_orden_entrega_endpoint(orden_entrega_data: dict, db: Session = Depends(get_db)):
    return create_orden_entrega(db, orden_entrega_data)
