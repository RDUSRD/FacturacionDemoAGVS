from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.factura.facturaService import create_factura

router = APIRouter()

@router.post("/factura")
def create_factura_endpoint(factura_data: dict, db: Session = Depends(get_db)):
    return create_factura(db, factura_data)
