from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.orden_entrega.ordenEntregaService import (
    get_orden_entrega_by_id,
    get_all_ordenes_entrega,
    get_or_create_orden_entrega,
    update_orden_entrega,
    # delete_orden_entrega,
)
from src.orden_entrega.ordenEntregaSchema import OrdenEntregaSchema, OrdenEntregaUpdateSchema

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

@router.post("/create")
def create_or_get_orden_entrega_endpoint(orden_entrega_data: OrdenEntregaSchema, db: Session = Depends(get_db)):
    return get_or_create_orden_entrega(db, orden_entrega_data)

@router.put("/{orden_entrega_id}")
def update_orden_entrega_endpoint(orden_entrega_id: int, orden_entrega_data: OrdenEntregaUpdateSchema, db: Session = Depends(get_db)):
    orden_entrega = update_orden_entrega(db, orden_entrega_id, orden_entrega_data)
    if not orden_entrega:
        raise HTTPException(status_code=404, detail="Orden de entrega no encontrada")
    return orden_entrega

# @router.delete("/{orden_entrega_id}")
# def delete_orden_entrega_endpoint(orden_entrega_id: int, db: Session = Depends(get_db)):
#     orden_entrega = delete_orden_entrega(db, orden_entrega_id)
#     if not orden_entrega:
#         raise HTTPException(status_code=404, detail="Orden de entrega no encontrada")
#     return {"detail": "Orden de entrega eliminada correctamente"}
