from sqlalchemy.orm import Session
from src.documento.factura.facModel import Factura
from src.documento.factura.iva.ivaModel import iva
from src.documento.factura.operacion.operacionModel import Operacion


def get_all_facturas(db: Session):
    return db.query(Factura).all()


def get_factura_by_id(db: Session, factura_id: int):
    return db.query(Factura).filter(Factura.id == factura_id).first()

def get_iva_by_factura_id(db: Session, factura_id: int):
    return db.query(iva).filter(iva.factura_id == factura_id).all()

def get_operaciones_by_factura_id(db: Session, factura_id: int):
    return db.query(Operacion).filter(Operacion.factura_id == factura_id).all()
