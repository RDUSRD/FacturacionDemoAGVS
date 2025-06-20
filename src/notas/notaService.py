from sqlalchemy.orm import Session
from src.notas.notaModel import NotaDebito, NotaCredito
from src.notas.notaSchema import (
    NotaDebitoSchema,
    NotaDebitoUpdateSchema,
    NotaCreditoSchema,
    NotaCreditoUpdateSchema,
)


# Servicio Nota de Débito
def get_all_notas_debito(db: Session):
    return db.query(NotaDebito).all()


def get_nota_debito_by_id(db: Session, nota_debito_id: int):
    return db.query(NotaDebito).filter(NotaDebito.id == nota_debito_id).first()


def get_or_create_nota_debito(db: Session, nota_debito_data: NotaDebitoSchema):
    nota_debito = (
        db.query(NotaDebito)
        .filter(
            NotaDebito.documento_relacionado_id
            == nota_debito_data.documento_relacionado_id
        )
        .first()
    )
    if not nota_debito:
        nota_debito = NotaDebito(**nota_debito_data.model_dump())
        db.add(nota_debito)
        db.commit()
        db.refresh(nota_debito)
    return nota_debito


def update_nota_debito(
    db: Session, nota_debito_id: int, nota_debito_data: NotaDebitoUpdateSchema
):
    nota_debito = db.query(NotaDebito).filter(NotaDebito.id == nota_debito_id).first()
    if nota_debito:
        for key, value in nota_debito_data.model_dump(exclude_unset=True).items():
            setattr(nota_debito, key, value)
        db.commit()
        db.refresh(nota_debito)
    return nota_debito


# def delete_nota_debito(db: Session, nota_debito_id: int):
#     nota_debito = db.query(NotaDebito).filter(NotaDebito.id == nota_debito_id).first()
#     if nota_debito:
#         db.delete(nota_debito)
#         db.commit()
#     return nota_debito


# Servicio Nota de Crédito
def get_all_notas_credito(db: Session):
    return db.query(NotaCredito).all()


def get_nota_credito_by_id(db: Session, nota_credito_id: int):
    return db.query(NotaCredito).filter(NotaCredito.id == nota_credito_id).first()


def get_or_create_nota_credito(db: Session, nota_credito_data: NotaCreditoSchema):
    nota_credito = (
        db.query(NotaCredito)
        .filter(
            NotaCredito.documento_relacionado_id
            == nota_credito_data.documento_relacionado_id
        )
        .first()
    )
    if not nota_credito:
        nota_credito = NotaCredito(**nota_credito_data.model_dump())
        db.add(nota_credito)
        db.commit()
        db.refresh(nota_credito)
    return nota_credito


def update_nota_credito(
    db: Session, nota_credito_id: int, nota_credito_data: NotaCreditoUpdateSchema
):
    nota_credito = (
        db.query(NotaCredito).filter(NotaCredito.id == nota_credito_id).first()
    )
    if nota_credito:
        for key, value in nota_credito_data.model_dump(exclude_unset=True).items():
            setattr(nota_credito, key, value)
        db.commit()
        db.refresh(nota_credito)
    return nota_credito


# def delete_nota_credito(db: Session, nota_credito_id: int):
#     nota_credito = (
#         db.query(NotaCredito).filter(NotaCredito.id == nota_credito_id).first()
#     )
#     if nota_credito:
#         db.delete(nota_credito)
#         db.commit()
#     return nota_credito
