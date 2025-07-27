from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from database import get_db
from src.auditoria.audService import (
    get_auditoria_by_id,
    get_all_auditorias,
)
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("AuditoriaRouter")

router = APIRouter(tags=["Auditoria"], prefix="/auditoria")


@router.get("/{auditoria_id}", response_model=dict)
def get_auditoria_endpoint(
    auditoria_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo auditoría con ID: {auditoria_id}", extra=request_info)
    auditoria = get_auditoria_by_id(db, auditoria_id)
    if not auditoria:
        logger.warning(
            f"Auditoría con ID: {auditoria_id} no encontrada", extra=request_info
        )
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return auditoria


@router.get("/", response_model=list)
def get_auditorias_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1),
    page: int = Query(1, ge=1),
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo auditorías con límite: {limit} y página: {page}",
        extra=request_info,
    )
    auditorias = get_all_auditorias(db, limit=limit, page=page)
    if not auditorias:
        logger.warning("No se encontraron auditorías", extra=request_info)
        raise HTTPException(status_code=404, detail="No se encontraron auditorías")
    return auditorias
