from sqlalchemy.orm import Session
from src.documento.notas.notaModel import NotaDebito, NotaCredito


# Servicio Nota de Débito
def get_all_notas_debito(db: Session):
    return db.query(NotaDebito).all()


def get_nota_debito_by_id(db: Session, nota_debito_id: int):
    return db.query(NotaDebito).filter(NotaDebito.nota_debito_id == nota_debito_id).first()

def get_nota_debito_by_factura(db: Session, factura_id: int):
    return db.query(NotaDebito).filter(NotaDebito.factura_id == factura_id).first()


# Servicio Nota de Crédito
def get_all_notas_credito(db: Session):
    return db.query(NotaCredito).all()


def get_nota_credito_by_id(db: Session, nota_credito_id: int):
    return db.query(NotaCredito).filter(NotaCredito.nota_credito_id == nota_credito_id).first()

def get_nota_credito_by_factura(db: Session, factura_id: int):
    return db.query(NotaCredito).filter(NotaCredito.factura_id == factura_id).first()
