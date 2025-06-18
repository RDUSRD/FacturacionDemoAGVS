from sqlalchemy.orm import Session
from src.documento.docModel import Documento

def get_documento_by_id(db: Session, documento_id: int):
    return db.query(Documento).filter(Documento.id == documento_id).first()
