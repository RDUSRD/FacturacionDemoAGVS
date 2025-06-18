from sqlalchemy.orm import Session
from src.notas.notaModel import NotaDebito, NotaCredito

def create_nota_debito(db: Session, nota_debito_data: dict):
    nota_debito = NotaDebito(**nota_debito_data)
    db.add(nota_debito)
    db.commit()
    db.refresh(nota_debito)
    return nota_debito

def create_nota_credito(db: Session, nota_credito_data: dict):
    nota_credito = NotaCredito(**nota_credito_data)
    db.add(nota_credito)
    db.commit()
    db.refresh(nota_credito)
    return nota_credito
