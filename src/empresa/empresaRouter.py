from fastapi import APIRouter, Depends, HTTPException, Request, Query
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
from src.loggers.loggerService import get_logger, get_request_info

# Crear una instancia del logger para el módulo de empresa
logger = get_logger("EmpresaRouter")

router = APIRouter(prefix="/empresa", tags=["Empresa"])


@router.get("/")
def get_empresas(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    request_info = get_request_info(request)
    logger.info("Obteniendo todas las empresas", extra=request_info)
    return get_all_empresas(db, limit=limit, offset=offset)


@router.get("/{empresa_id}")
def get_empresa(empresa_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo empresa con ID: {empresa_id}", extra=request_info)
    empresa = get_empresa_by_id(db, empresa_id)
    if not empresa:
        logger.warning(f"Empresa con ID: {empresa_id} no encontrada", extra=request_info)
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


@router.post("/create")
def create_or_get_empresa(
    empresa_data: EmpresaSchema, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info("Creando o obteniendo empresa", extra=request_info)
    return get_or_create_empresa(db, empresa_data)


@router.put("/{empresa_id}")
def update_empresa_endpoint(
    empresa_id: int,
    empresa_data: EmpresaUpdateSchema,
    request: Request,
    db: Session = Depends(get_db),
):
    request_info = get_request_info(request)
    logger.info(f"Actualizando empresa con ID: {empresa_id}", extra=request_info)
    empresa = update_empresa(db, empresa_id, empresa_data)
    if not empresa:
        logger.warning(
            f"Empresa con ID: {empresa_id} no encontrada para actualizar",
            extra=request_info,
        )
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa


# @router.delete("/{empresa_id}")
# def delete_empresa_endpoint(empresa_id: int, db: Session = Depends(get_db)):
#     logger.info(f"Eliminando empresa con ID {empresa_id}", extra={"user": "Anonymous", "ip": "UnknownIP"})
#     empresa = delete_empresa(db, empresa_id)
#     if not empresa:
#         logger.warning(f"Empresa con ID {empresa_id} no encontrada para eliminar", extra={"user": "Anonymous", "ip": "UnknownIP"})
#         raise HTTPException(status_code=404, detail="Empresa no encontrada")
#     return {"detail": "Empresa eliminada correctamente"}
