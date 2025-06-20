from sqlalchemy.orm import Session
from src.orden_entrega.ordenEntregaModel import OrdenEntrega
from src.orden_entrega.ordenEntregaSchema import (
    OrdenEntregaSchema,
    OrdenEntregaUpdateSchema,
)


def get_all_ordenes_entrega(db: Session):
    return db.query(OrdenEntrega).all()


def get_orden_entrega_by_id(db: Session, orden_entrega_id: int):
    return db.query(OrdenEntrega).filter(OrdenEntrega.id == orden_entrega_id).first()


def get_or_create_orden_entrega(db: Session, orden_entrega_data: OrdenEntregaSchema):
    orden_entrega = (
        db.query(OrdenEntrega).filter(OrdenEntrega.id == orden_entrega_data.id).first()
    )
    if not orden_entrega:
        orden_entrega = OrdenEntrega(**orden_entrega_data.model_dump())
        db.add(orden_entrega)
        db.commit()
        db.refresh(orden_entrega)
    return orden_entrega


def update_orden_entrega(
    db: Session, orden_entrega_id: int, orden_entrega_data: OrdenEntregaUpdateSchema
):
    orden_entrega = (
        db.query(OrdenEntrega).filter(OrdenEntrega.id == orden_entrega_id).first()
    )
    if orden_entrega:
        for key, value in orden_entrega_data.model_dump(exclude_unset=True).items():
            setattr(orden_entrega, key, value)
        db.commit()
        db.refresh(orden_entrega)
    return orden_entrega


# def delete_orden_entrega(db: Session, orden_entrega_id: int):
#     orden_entrega = (
#         db.query(OrdenEntrega).filter(OrdenEntrega.id == orden_entrega_id).first()
#     )
#     if orden_entrega:
#         db.delete(orden_entrega)
#         db.commit()
#     return orden_entrega
