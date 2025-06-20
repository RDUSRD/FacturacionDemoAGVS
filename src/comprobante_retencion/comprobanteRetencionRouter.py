from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.comprobante_retencion.comprobanteRetencionService import (
    get_comprobante_retencion_by_id,
    get_all_comprobantes_retencion,
    get_or_create_comprobante_retencion,
    update_comprobante_retencion,
    # delete_comprobante_retencion,
)
from src.comprobante_retencion.comprobanteRetencionSchema import ComprobanteRetencionSchema, ComprobanteRetencionUpdateSchema

router = APIRouter(prefix="/comprobante_retencion", tags=["ComprobanteRetencion"])

@router.get("/")
def get_comprobantes_retencion(db: Session = Depends(get_db)):
    return get_all_comprobantes_retencion(db)

@router.get("/{comprobante_retencion_id}")
def get_comprobante_retencion(comprobante_retencion_id: int, db: Session = Depends(get_db)):
    comprobante_retencion = get_comprobante_retencion_by_id(db, comprobante_retencion_id)
    if not comprobante_retencion:
        raise HTTPException(status_code=404, detail="Comprobante de retención no encontrado")
    return comprobante_retencion

@router.post("/create")
def create_or_get_comprobante_retencion_endpoint(comprobante_retencion_data: ComprobanteRetencionSchema, db: Session = Depends(get_db)):
    return get_or_create_comprobante_retencion(db, comprobante_retencion_data)

@router.put("/{comprobante_retencion_id}")
def update_comprobante_retencion_endpoint(comprobante_retencion_id: int, comprobante_retencion_data: ComprobanteRetencionUpdateSchema, db: Session = Depends(get_db)):
    comprobante_retencion = update_comprobante_retencion(db, comprobante_retencion_id, comprobante_retencion_data)
    if not comprobante_retencion:
        raise HTTPException(status_code=404, detail="Comprobante de retención no encontrado")
    return comprobante_retencion

# @router.delete("/{comprobante_retencion_id}")
# def delete_comprobante_retencion_endpoint(comprobante_retencion_id: int, db: Session = Depends(get_db)):
#     comprobante_retencion = delete_comprobante_retencion(db, comprobante_retencion_id)
#     if not comprobante_retencion:
#         raise HTTPException(status_code=404, detail="Comprobante de retención no encontrado")
#     return {"detail": "Comprobante de retención eliminado correctamente"}
