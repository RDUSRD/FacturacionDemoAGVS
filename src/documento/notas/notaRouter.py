from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from database import get_db
from src.documento.notas.notaService import (
    get_nota_credito_by_factura,
    get_nota_debito_by_factura,
    get_nota_debito_by_id,
    get_all_notas_debito,
    get_nota_credito_by_id,
    get_all_notas_credito,
)
from src.loggers.loggerService import get_logger, get_request_info

router = APIRouter(prefix="/notas", tags=["Notas"])
logger = get_logger("notaRouter")


# Rutas para Notas de Débito
@router.get("/nota_debito")
def route_get_notas_debito(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    request_info = get_request_info(request)
    logger.info("Solicitud para obtener todas las notas de débito", extra=request_info)
    notas_debito = get_all_notas_debito(db, limit=limit, offset=offset)
    if not notas_debito:
        logger.warning("No se encontraron notas de débito", extra=request_info)
        return {"error": "No se encontraron notas de débito"}
    return notas_debito


@router.get("/nota_debito/{nota_debito_id}")
def route_get_nota_debito(
    nota_debito_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Solicitud para obtener la nota de débito con ID {nota_debito_id}",
        extra=request_info,
    )
    nota_debito = get_nota_debito_by_id(db, nota_debito_id)
    if not nota_debito:
        logger.error(
            f"Nota de débito con ID {nota_debito_id} no encontrada", extra=request_info
        )
        return {"error": "Nota de débito no encontrada"}
    logger.info(f"Nota de débito encontrada: {nota_debito}", extra=request_info)
    return nota_debito


@router.get("/nota_debito/factura/{factura_id}")
def route_get_nota_debito_by_factura(
    factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Solicitud para obtener la nota de débito con factura ID {factura_id}",
        extra=request_info,
    )
    nota_debito = get_nota_debito_by_factura(db, factura_id)
    if not nota_debito:
        logger.error(
            f"Nota de débito con factura ID {factura_id} no encontrada",
            extra=request_info,
        )
        return {"error": "Nota de débito no encontrada"}
    logger.info(f"Nota de débito encontrada: {nota_debito}", extra=request_info)
    return nota_debito


# Rutas para Notas de Crédito
@router.get("/nota_credito")
def route_get_notas_credito(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    request_info = get_request_info(request)
    logger.info("Solicitud para obtener todas las notas de crédito", extra=request_info)
    notas_credito = get_all_notas_credito(db, limit=limit, offset=offset)
    if not notas_credito:
        logger.warning("No se encontraron notas de crédito", extra=request_info)
        return {"error": "No se encontraron notas de crédito"}
    return notas_credito


@router.get("/nota_credito/{nota_credito_id}")
def route_get_nota_credito(
    nota_credito_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Solicitud para obtener la nota de crédito con ID {nota_credito_id}",
        extra=request_info,
    )
    nota_credito = get_nota_credito_by_id(db, nota_credito_id)
    if not nota_credito:
        logger.error(
            f"Nota de crédito con ID {nota_credito_id} no encontrada",
            extra=request_info,
        )
        return {"error": "Nota de crédito no encontrada"}
    logger.info(f"Nota de crédito encontrada: {nota_credito}", extra=request_info)
    return nota_credito


@router.get("/nota_credito/factura/{factura_id}")
def route_get_nota_credito_by_factura(
    factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Solicitud para obtener la nota de crédito con factura ID {factura_id}",
        extra=request_info,
    )
    nota_credito = get_nota_credito_by_factura(db, factura_id)
    if not nota_credito:
        logger.error(
            f"Nota de crédito con factura ID {factura_id} no encontrada",
            extra=request_info,
        )
        return {"error": "Nota de crédito no encontrada"}
    logger.info(f"Nota de crédito encontrada: {nota_credito}", extra=request_info)
    return nota_credito
