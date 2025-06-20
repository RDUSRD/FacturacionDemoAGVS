from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.factura.facturaService import (
    get_factura_by_id,
    get_all_facturas,
    get_operaciones_by_factura_id,
    get_iva_by_factura_id,
)



router = APIRouter(prefix="/factura", tags=["Factura"])


@router.get("/")
def get_facturas(db: Session = Depends(get_db)):
    return get_all_facturas(db)


@router.get("/{factura_id}")
def get_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = get_factura_by_id(db, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

# Endnpoints para obtener IVA y operaciones asociadas a una factura
@router.get("/{factura_id}/iva")
def fetch_iva_by_factura_id(factura_id: int, db: Session = Depends(get_db)):
    iva = get_iva_by_factura_id(db, factura_id)
    if not iva:
        raise HTTPException(status_code=404, detail="IVA no encontrado para la factura")
    return iva

@router.get("/{factura_id}/operaciones")
def fetch_operaciones_by_factura_id(factura_id: int, db: Session = Depends(get_db)):
    operaciones = get_operaciones_by_factura_id(db, factura_id)
    if not operaciones:
        raise HTTPException(status_code=404, detail="Operaciones no encontradas para la factura")
    return operaciones