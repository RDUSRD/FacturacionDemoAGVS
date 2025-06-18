from sqlalchemy.orm import Session
from src.auditoria.audModel import Auditoria

def log_auditoria(db: Session, auditoria_data: dict):
    auditoria = Auditoria(**auditoria_data)
    db.add(auditoria)
    db.commit()
    db.refresh(auditoria)
    return auditoria
