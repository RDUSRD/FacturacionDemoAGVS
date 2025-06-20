from sqlalchemy.orm import Session
from src.documento.orden_entrega.ordenEntregaModel import OrdenEntrega


def get_all_ordenes_entrega(db: Session):
    return db.query(OrdenEntrega).all()


def get_orden_entrega_by_id(db: Session, orden_entrega_id: int):
    return db.query(OrdenEntrega).filter(OrdenEntrega.id == orden_entrega_id).first()