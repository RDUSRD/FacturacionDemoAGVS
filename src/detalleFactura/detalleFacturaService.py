from sqlalchemy.orm import Session
from src.detalleFactura.detalleFacturaModel import DetalleFactura
from src.detalleFactura.detalleFacturaSchema import (
    DetalleFacturaSchema,
    DetalleFacturaUpdateSchema,
)


def get_all_detalles_factura(db: Session):
    return db.query(DetalleFactura).all()


def get_detalle_factura_by_id(db: Session, detalle_factura_id: int):
    return (
        db.query(DetalleFactura).filter(DetalleFactura.id == detalle_factura_id).first()
    )


def get_or_create_detalle_factura(
    db: Session, detalle_factura_data: DetalleFacturaSchema
):
    detalle_factura = (
        db.query(DetalleFactura)
        .filter(
            DetalleFactura.factura_id == detalle_factura_data.factura_id,
            DetalleFactura.producto_id == detalle_factura_data.producto_id,
        )
        .first()
    )
    if not detalle_factura:
        detalle_factura = DetalleFactura(**detalle_factura_data.model_dump())
        db.add(detalle_factura)
        db.commit()
        db.refresh(detalle_factura)
    return detalle_factura


def update_detalle_factura(
    db: Session,
    detalle_factura_id: int,
    detalle_factura_data: DetalleFacturaUpdateSchema,
):
    detalle_factura = (
        db.query(DetalleFactura).filter(DetalleFactura.id == detalle_factura_id).first()
    )
    if detalle_factura:
        for key, value in detalle_factura_data.model_dump(exclude_unset=True).items():
            setattr(detalle_factura, key, value)
        db.commit()
        db.refresh(detalle_factura)
    return detalle_factura
