from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from src.documento.factura.detalleFactura.detalleFacturaService import (
    get_detalle_factura_by_id,
    get_all_detalles_factura,
)
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("DetalleFacturaRouter")

router = APIRouter(prefix="/detalle_factura", tags=["DetalleFactura"])


@router.get("/")
def get_detalles_factura(request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Obteniendo todos los detalles de factura", extra=request_info)
    return get_all_detalles_factura(db)


@router.get("/{detalle_factura_id}")
def get_detalle_factura(
    detalle_factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo detalle de factura con ID: {detalle_factura_id}", extra=request_info
    )
    detalle_factura = get_detalle_factura_by_id(db, detalle_factura_id)
    if not detalle_factura:
        logger.warning(
            f"Detalle de factura con ID: {detalle_factura_id} no encontrado",
            extra=request_info,
        )
        raise HTTPException(status_code=404, detail="Detalle de factura no encontrado")
    return detalle_factura
