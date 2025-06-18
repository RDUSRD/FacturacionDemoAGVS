from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.detalleFactura.detalleFacturaService import create_detalle_factura

router = APIRouter()

@router.post("/detalle_factura")
def create_detalle_factura_endpoint(detalle_factura_data: dict, db: Session = Depends(get_db)):
    return create_detalle_factura(db, detalle_factura_data)
