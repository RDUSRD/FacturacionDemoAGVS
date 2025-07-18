from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.factura.detalleFactura.detalleFacturaService import (
    get_detalle_factura_by_id,
    get_all_detalles_factura,
)

router = APIRouter(prefix="/detalle_factura", tags=["DetalleFactura"])


@router.get("/")
def get_detalles_factura(db: Session = Depends(get_db)):
    return get_all_detalles_factura(db)


@router.get("/{detalle_factura_id}")
def get_detalle_factura(detalle_factura_id: int, db: Session = Depends(get_db)):
    detalle_factura = get_detalle_factura_by_id(db, detalle_factura_id)
    if not detalle_factura:
        raise HTTPException(status_code=404, detail="Detalle de factura no encontrado")
    return detalle_factura
