from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.factura.facturaService import (
    get_factura_by_id,
    get_all_facturas,
    get_or_create_factura,
    update_factura,
    # delete_factura,
)
from src.factura.facturaSchema import FacturaSchema, FacturaUpdateSchema

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

@router.post("/create")
def create_or_get_factura_endpoint(factura_data: FacturaSchema, db: Session = Depends(get_db)):
    return get_or_create_factura(db, factura_data)

@router.put("/{factura_id}")
def update_factura_endpoint(factura_id: int, factura_data: FacturaUpdateSchema, db: Session = Depends(get_db)):
    factura = update_factura(db, factura_id, factura_data)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

# @router.delete("/{factura_id}")
# def delete_factura_endpoint(factura_id: int, db: Session = Depends(get_db)):
#     factura = delete_factura(db, factura_id)
#     if not factura:
#         raise HTTPException(status_code=404, detail="Factura no encontrada")
#     return {"detail": "Factura eliminada correctamente"}
