from sqlalchemy.orm import Session
from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura


def get_all_detalles_factura(db: Session):
    return db.query(DetalleFactura).all()


def get_detalle_factura_by_id(db: Session, detalle_factura_id: int):
    return (
        db.query(DetalleFactura).filter(DetalleFactura.id == detalle_factura_id).first()
    )
