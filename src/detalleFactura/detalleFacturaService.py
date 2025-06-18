from sqlalchemy.orm import Session
from src.detalleFactura.detalleFacturaModel import DetalleFactura

def create_detalle_factura(db: Session, detalle_factura_data: dict):
    detalle_factura = DetalleFactura(**detalle_factura_data)
    db.add(detalle_factura)
    db.commit()
    db.refresh(detalle_factura)
    return detalle_factura
