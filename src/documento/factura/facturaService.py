from sqlalchemy.orm import Session, joinedload
from src.pedidos.pedidoModel import Pedido
from src.documento.factura.facModel import Factura
from src.documento.factura.iva.ivaModel import iva
from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura


def get_all_facturas(db: Session, limit: int = 10, offset: int = 0):
    return db.query(Factura).offset(offset).limit(limit).all()


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
        pedido = db.query(Pedido).filter(Pedido.id == factura.pedido_id).first()
        return {
            "factura": factura,
            "detalles_factura": detalles_factura,
            "impuestos": impuestos,
            "pedido": pedido,
        }
    return None


def get_factura_by_numero_control(db: Session, numero_control: str):
    return db.query(Factura).filter(Factura.numero_control == numero_control).first()


def get_facturas_by_empresa_id(db: Session, empresa_id: int, limit: int = 10, offset: int = 0):
    return db.query(Factura).filter(Factura.empresa_id == empresa_id).offset(offset).limit(limit).all()


def get_facturas_by_cliente_id(db: Session, cliente_id: int, limit: int = 10, offset: int = 0):
    return db.query(Factura).filter(Factura.cliente_id == cliente_id).offset(offset).limit(limit).all()


def get_iva_by_factura_id(db: Session, factura_id: int):
    return db.query(iva).filter(iva.factura_id == factura_id).all()


def get_detalles_factura_by_factura_id(db: Session, factura_id: int):
    return (
        db.query(DetalleFactura).filter(DetalleFactura.factura_id == factura_id).all()
    )


def get_pedido_by_factura_id(db: Session, factura_id: int):
    pedido = (
        db.query(Pedido)
        .options(joinedload(Pedido.detalles))  # Cargar la relación detalles
        .join(Factura, Pedido.id == Factura.pedido_id)
        .filter(Factura.factura_id == factura_id)
        .first()
    )
    if pedido:
        return {"pedido": pedido}  # El pedido incluirá los detalles
    return None
