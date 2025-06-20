from sqlalchemy.orm import Session
from src.comprobante_retencion.comprobanteRetencionModel import ComprobanteRetencion
from src.comprobante_retencion.comprobanteRetencionSchema import (
    ComprobanteRetencionSchema,
    ComprobanteRetencionUpdateSchema,
)
from src.documento.documentoService import get_documento_by_id


def get_all_comprobantes_retencion(db: Session):
    return db.query(ComprobanteRetencion).all()


def get_comprobante_retencion_by_id(db: Session, comprobante_retencion_id: int):
    return (
        db.query(ComprobanteRetencion)
        .filter(ComprobanteRetencion.id == comprobante_retencion_id)
        .first()
    )


def get_or_create_comprobante_retencion(
    db: Session, comprobante_retencion_data: ComprobanteRetencionSchema
):
    comprobante_retencion = (
        db.query(ComprobanteRetencion)
        .filter(
            ComprobanteRetencion.documento_relacionado_id
            == comprobante_retencion_data.documento_relacionado_id
        )
        .first()
    )
    if not comprobante_retencion:
        # Verificamos si el documento relacionado existe
        documento = get_documento_by_id(
            db, comprobante_retencion_data.documento_relacionado_id
        )
        if not documento:
            raise ValueError(
                "El documento_relacionado_id es requerido para crear un comprobante de retención."
            )

        comprobante_retencion = ComprobanteRetencion(
            **comprobante_retencion_data.model_dump()
        )
        comprobante_retencion.documento_relacionado_id = documento.id
        # Aqui se puede agregar la lógica para calcular el monto total si es necesario
        # comprobante_retencion.monto_total = calcular_monto_total(comprobante_retencion)
        db.add(comprobante_retencion)
        db.commit()
        db.refresh(comprobante_retencion)
    return comprobante_retencion


def update_comprobante_retencion(
    db: Session,
    comprobante_retencion_id: int,
    comprobante_retencion_data: ComprobanteRetencionUpdateSchema,
):
    comprobante_retencion = (
        db.query(ComprobanteRetencion)
        .filter(ComprobanteRetencion.id == comprobante_retencion_id)
        .first()
    )
    if comprobante_retencion:
        # Verificamos si el documento relacionado existe
        documento = get_documento_by_id(
            db, comprobante_retencion_data.documento_relacionado_id
        )
        if not documento:
            raise ValueError(
                "El documento_relacionado_id es requerido para crear un comprobante de retención."
            )

        # Asignamos el ID del documento relacionado al comprobante de retención
        comprobante_retencion.documento_relacionado_id = documento.id

        # Actualizamos los campos del comprobante de retención
        for key, value in comprobante_retencion_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(comprobante_retencion, key, value)
        db.commit()
        db.refresh(comprobante_retencion)
    return comprobante_retencion


# def delete_comprobante_retencion(db: Session, comprobante_retencion_id: int):
#     comprobante_retencion = (
#         db.query(ComprobanteRetencion)
#         .filter(ComprobanteRetencion.id == comprobante_retencion_id)
#         .first()
#     )
#     if comprobante_retencion:
#         db.delete(comprobante_retencion)
#         db.commit()
#     return comprobante_retencion
