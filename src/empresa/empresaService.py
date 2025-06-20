from sqlalchemy.orm import Session
from src.empresa.empModel import Empresa
from src.empresa.empresaSchema import EmpresaSchema, EmpresaUpdateSchema


def get_all_empresas(db: Session):
    return db.query(Empresa).all()


def get_empresa_by_id(db: Session, empresa_id: int):
    return db.query(Empresa).filter(Empresa.id == empresa_id).first()


def get_or_create_empresa(db: Session, empresa_data: EmpresaSchema):
    empresa = db.query(Empresa).filter(Empresa.rif == empresa_data.rif).first()
    if not empresa:
        empresa = Empresa(**empresa_data.model_dump())
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        return empresa
    return {'message': 'Empresa ya existe ' + empresa.rif, 'empresa': empresa}


def update_empresa(db: Session, empresa_id: int, empresa_data: EmpresaUpdateSchema):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa:
        for key, value in empresa_data.model_dump(exclude_unset=True).items():
            setattr(empresa, key, value)
        db.commit()
        db.refresh(empresa)
    return empresa


# def delete_empresa(db: Session, empresa_id: int):
#     empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
#     if empresa:
#         db.delete(empresa)
#         db.commit()
#     return empresa
