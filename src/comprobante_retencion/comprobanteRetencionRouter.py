from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.comprobante_retencion.comprobanteRetencionService import create_comprobante_retencion

router = APIRouter()

@router.post("/comprobante_retencion")
def create_comprobante_retencion_endpoint(comprobante_retencion_data: dict, db: Session = Depends(get_db)):
    return create_comprobante_retencion(db, comprobante_retencion_data)
