from sqlalchemy.orm import Session
from src.documento.notas.notaModel import NotaDebito, NotaCredito


# Servicio Nota de Débito
def get_all_notas_debito(db: Session):
    return db.query(NotaDebito).all()


def get_nota_debito_by_id(db: Session, nota_debito_id: int):
    return db.query(NotaDebito).filter(NotaDebito.id == nota_debito_id).first()


# Servicio Nota de Crédito
def get_all_notas_credito(db: Session):
    return db.query(NotaCredito).all()


def get_nota_credito_by_id(db: Session, nota_credito_id: int):
    return db.query(NotaCredito).filter(NotaCredito.id == nota_credito_id).first()
