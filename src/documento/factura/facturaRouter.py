from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.factura.facturaService import (
    get_documentos_by_cliente_id,
    get_documentos_by_empresa_id,
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


@router.get("/numero-control/{numero_control}")
def get_factura_by_numero_control(numero_control: str, db: Session = Depends(get_db)):
    factura = get_factura_by_numero_control(db, numero_control)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@router.get("/empresa/{empresa_id}")
def get_facturas_by_empresa_id(empresa_id: int, db: Session = Depends(get_db)):
    facturas = get_documentos_by_empresa_id(db, empresa_id)
    if not facturas:
        raise HTTPException(
            status_code=404, detail="No se encontraron facturas para la empresa"
        )
    return facturas


@router.get("/cliente/{cliente_id}")
def get_facturas_by_cliente_id(cliente_id: int, db: Session = Depends(get_db)):
    facturas = get_documentos_by_cliente_id(db, cliente_id)
    if not facturas:
        raise HTTPException(
            status_code=404, detail="No se encontraron facturas para el cliente"
        )
    return facturas


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
        raise HTTPException(
            status_code=404, detail="Operaciones no encontradas para la factura"
        )
    return operaciones
