from sqlalchemy.orm import Session
from src.auditoria.audModel import Auditoria

def get_auditoria_by_id(db: Session, auditoria_id: int):
    try:
        auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
        return auditoria.to_dict() if auditoria else None
    except Exception as e:
        return f"Error al obtener auditoria: {e}"

# Function to get all auditorias with pagination to avoid performance issues and test for others endpoints
def get_all_auditorias(db: Session, limit: int = 100, page: int = 1): 
    try:
        offset = (page - 1) * limit
        auditorias = db.query(Auditoria).offset(offset).limit(limit).all()
        return [auditoria.to_dict() for auditoria in auditorias]
    except Exception as e:
        return f"Error al obtener auditorias: {e}"
