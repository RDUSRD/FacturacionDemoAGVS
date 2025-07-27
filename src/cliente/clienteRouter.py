from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.cliente.clienteSchema import ClienteSchema, ClienteUpdateSchema
from database import get_db
from src.cliente.clienteService import (
    get_cliente_by_id,
    get_all_clientes,
    get_or_create_cliente,
    update_cliente,
    # delete_cliente,
)
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("ClienteRouter")

router = APIRouter(prefix="/cliente", tags=["Cliente"])


@router.get("/")
def get_clientes(request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Obteniendo todos los clientes", extra=request_info)
    return get_all_clientes(db)


@router.get("/{cliente_id}")
def get_cliente(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo cliente con ID: {cliente_id}", extra=request_info)
    cliente = get_cliente_by_id(db, cliente_id)
    if not cliente:
        logger.warning(f"Cliente con ID: {cliente_id} no encontrado", extra=request_info)
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/create")
def create_or_get_cliente(cliente_data: ClienteSchema, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Creando o obteniendo cliente", extra=request_info)
    return get_or_create_cliente(db, cliente_data)


@router.put("/{cliente_id}")
def update_cliente_endpoint(
    cliente_id: int, cliente_data: ClienteUpdateSchema, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(f"Actualizando cliente con ID: {cliente_id}", extra=request_info)
    cliente = update_cliente(db, cliente_id, cliente_data)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


# @router.delete("/{cliente_id}")
# def delete_cliente_endpoint(cliente_id: int, db: Session = Depends(get_db)):
#     cliente = delete_cliente(db, cliente_id)
#     if not cliente:
#         raise HTTPException(status_code=404, detail="Cliente no encontrado")
#     return {"detail": "Cliente eliminado correctamente"}
