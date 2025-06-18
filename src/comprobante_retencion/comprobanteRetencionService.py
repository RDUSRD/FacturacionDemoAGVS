from sqlalchemy.orm import Session
from src.comprobante_retencion.comprobanteRetencionModel import ComprobanteRetencion

def create_comprobante_retencion(db: Session, comprobante_retencion_data: dict):
    comprobante_retencion = ComprobanteRetencion(**comprobante_retencion_data)
    db.add(comprobante_retencion)
    db.commit()
    db.refresh(comprobante_retencion)
    return comprobante_retencion
