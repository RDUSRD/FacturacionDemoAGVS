from sqlalchemy.orm import Session
from src.empresa.empModel import Empresa

def get_or_create_empresa(db: Session, empresa_data: dict):
    empresa = db.query(Empresa).filter(Empresa.rif == empresa_data["rif"]).first()
    if not empresa:
        empresa = Empresa(**empresa_data)
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
    return empresa
