from sqlalchemy.orm import Session
from src.detalleFactura.detalleFacturaModel import DetalleFactura
from src.detalleFactura.detalleFacturaSchema import (
    DetalleFacturaSchema,
    DetalleFacturaUpdateSchema,
)
from src.documento.factura.facturaService import get_factura_by_id
from src.producto.productoService import get_producto_by_id


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
        # Verificamos si existe la factura
        factura = get_factura_by_id(db, detalle_factura_data.factura_id)
        if not factura:
            return {
                "error": "La factura_id no existe y es requerida para crear un detalle de factura."
            }

        producto = get_producto_by_id(db, detalle_factura_data.producto_id)
        if not producto:
            return {
                "error": "La producto_id no existe y es requerida para crear un detalle de factura."
            }

        if detalle_factura_data.cantidad <= 0:
            return {"error": "La cantidad debe ser mayor a 0."}

        # calcular el total
        total = detalle_factura_data.cantidad * producto.precio

        detalle_factura = DetalleFactura(**detalle_factura_data.model_dump())
        detalle_factura.total = total
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
        # Calcular el total si la cantidad ha cambiado
        if detalle_factura_data.cantidad is not None:
            producto = get_producto_by_id(db, detalle_factura.producto_id)
            if producto:
                total = detalle_factura_data.cantidad * producto.precio
                detalle_factura.total = total
        for key, value in detalle_factura_data.model_dump(exclude_unset=True).items():
            setattr(detalle_factura, key, value)
        db.commit()
        db.refresh(detalle_factura)
        return detalle_factura
    else:
        return {"error": "El detalle de factura con el ID especificado no existe."}
