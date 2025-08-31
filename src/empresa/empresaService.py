from datetime import datetime
from sqlalchemy.orm import Session
from src.empresa.empModel import Empresa
from src.empresa.empresaSchema import EmpresaSchema, EmpresaUpdateSchema


def get_all_empresas(db: Session, limit: int = 10, offset: int = 0):
    return db.query(Empresa).offset(offset).limit(limit).all()


def get_empresa_by_id(db: Session, empresa_id: int):
    return db.query(Empresa).filter(Empresa.id == empresa_id).first()


def get_empresa_by_rif(db: Session, rif: str):
    return db.query(Empresa).filter(Empresa.rif == rif).first()


def get_or_create_empresa(db: Session, empresa_data: EmpresaSchema):
    empresa = db.query(Empresa).filter(Empresa.rif == empresa_data.rif).first()
    if not empresa:
        empresa = Empresa(**empresa_data.model_dump())
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        return empresa
    return {"message": "Empresa ya existe " + empresa.rif, "empresa": empresa}


def update_empresa(db: Session, empresa_id: int, empresa_data: EmpresaUpdateSchema):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa:
        for key, value in empresa_data.model_dump(exclude_unset=True).items():
            setattr(empresa, key, value)
        date_updated = empresa_data.date_updated or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        empresa.date_updated = date_updated
        db.commit()
        db.refresh(empresa)
    return empresa


# def delete_empresa(db: Session, empresa_id: int):
#     empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
#     if empresa:
#         db.delete(empresa)
#         db.commit()
#     return empresa
