from sqlalchemy.orm import Session
from src.documento.factura.facModel import Factura
from src.documento.factura.iva.ivaModel import iva
from src.documento.factura.operacion.operacionModel import Operacion
from src.detalleFactura.detalleFacturaModel import DetalleFactura


def get_all_facturas(db: Session):
    return db.query(Factura).all()


def get_factura_by_id(db: Session, factura_id: int):
    """Obtiene una factura por ID junto con sus relaciones: detalles, impuestos y operaciones."""
    factura = db.query(Factura).filter(Factura.factura_id == factura_id).first()
    if factura:
        detalles_factura = (
            db.query(DetalleFactura)
            .filter(DetalleFactura.factura_id == factura_id)
            .all()
        )
        impuestos = db.query(iva).filter(iva.factura_id == factura_id).all()
        operaciones = (
            db.query(Operacion).filter(Operacion.factura_id == factura_id).all()
        )
        return {
            "factura": factura,
            "detalles_factura": detalles_factura,
            "impuestos": impuestos,
            "operaciones": operaciones,
        }
    return None


def get_factura_by_numero_control(db: Session, numero_control: str):
    return db.query(Factura).filter(Factura.numero_control == numero_control).first()


def get_documentos_by_empresa_id(db: Session, empresa_id: int):
    return db.query(Factura).filter(Factura.empresa_id == empresa_id).all()


def get_documentos_by_cliente_id(db: Session, cliente_id: int):
    return db.query(Factura).filter(Factura.cliente_id == cliente_id).all()


def get_iva_by_factura_id(db: Session, factura_id: int):
    return db.query(iva).filter(iva.factura_id == factura_id).all()


def get_operaciones_by_factura_id(db: Session, factura_id: int):
    return db.query(Operacion).filter(Operacion.factura_id == factura_id).all()
