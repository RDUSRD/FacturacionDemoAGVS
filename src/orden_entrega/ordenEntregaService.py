from sqlalchemy.orm import Session
from src.orden_entrega.ordenEntregaModel import OrdenEntrega

def create_orden_entrega(db: Session, orden_entrega_data: dict):
    orden_entrega = OrdenEntrega(**orden_entrega_data)
    db.add(orden_entrega)
    db.commit()
    db.refresh(orden_entrega)
    return orden_entrega
