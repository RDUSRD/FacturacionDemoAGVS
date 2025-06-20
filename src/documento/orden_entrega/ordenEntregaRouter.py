from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.orden_entrega.ordenEntregaService import (
    get_orden_entrega_by_id,
    get_all_ordenes_entrega,
)

router = APIRouter(prefix="/orden_entrega", tags=["OrdenEntrega"])


@router.get("/")
def get_ordenes_entrega(db: Session = Depends(get_db)):
    return get_all_ordenes_entrega(db)


@router.get("/{orden_entrega_id}")
def get_orden_entrega(orden_entrega_id: int, db: Session = Depends(get_db)):
    orden_entrega = get_orden_entrega_by_id(db, orden_entrega_id)
    if not orden_entrega:
        raise HTTPException(status_code=404, detail="Orden de entrega no encontrada")
    return orden_entrega
