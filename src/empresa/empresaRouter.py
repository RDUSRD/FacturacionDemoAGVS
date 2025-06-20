from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.empresa.empresaService import (
    get_empresa_by_id,
    get_all_empresas,
    get_or_create_empresa,
    update_empresa,
    # delete_empresa,
)
from src.empresa.empresaSchema import EmpresaSchema, EmpresaUpdateSchema

router = APIRouter(prefix="/empresa", tags=["Empresa"])

@router.get("/")
def get_empresas(db: Session = Depends(get_db)):
    return get_all_empresas(db)

@router.get("/{empresa_id}")
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = get_empresa_by_id(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

@router.post("/create")
def create_or_get_empresa(empresa_data: EmpresaSchema, db: Session = Depends(get_db)):
    return get_or_create_empresa(db, empresa_data)

@router.put("/{empresa_id}")
def update_empresa_endpoint(empresa_id: int, empresa_data: EmpresaUpdateSchema, db: Session = Depends(get_db)):
    empresa = update_empresa(db, empresa_id, empresa_data)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

# @router.delete("/{empresa_id}")
# def delete_empresa_endpoint(empresa_id: int, db: Session = Depends(get_db)):
#     empresa = delete_empresa(db, empresa_id)
#     if not empresa:
#         raise HTTPException(status_code=404, detail="Empresa no encontrada")
#     return {"detail": "Empresa eliminada correctamente"}
