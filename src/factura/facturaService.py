from sqlalchemy.orm import Session
from src.factura.facModel import Factura

def create_factura(db: Session, factura_data: dict):
    factura = Factura(**factura_data)
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura
