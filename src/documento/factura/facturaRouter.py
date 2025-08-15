from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from src.documento.factura.facturaService import (
    get_documentos_by_cliente_id,
    get_documentos_by_empresa_id,
    get_factura_by_id,
    get_all_facturas,
    get_iva_by_factura_id,
    get_detalles_factura_by_factura_id,
    get_factura_by_numero_control,
    get_pedido_by_factura_id,
)
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("FacturaRouter")
router = APIRouter(prefix="/factura", tags=["Factura"])


@router.get("/")
def get_facturas(request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Obteniendo todas las facturas", extra=request_info)
    return get_all_facturas(db)


@router.get("/{factura_id}")
def get_factura(factura_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo factura con ID: {factura_id}", extra=request_info)
    factura = get_factura_by_id(db, factura_id)
    if not factura:
        logger.warning(
            f"Factura con ID: {factura_id} no encontrada", extra=request_info
        )
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@router.get("/numero-control/{numero_control}")
def get_factura_by_numero_control_route(
    numero_control: str, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo factura con número de control: {numero_control}",
        extra=request_info,
    )
    factura = get_factura_by_numero_control(db, numero_control)
    if not factura:
        logger.warning(
            f"Factura con número de control: {numero_control} no encontrada",
            extra=request_info,
        )
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@router.get("/empresa/{empresa_id}")
def get_facturas_by_empresa_id(
    empresa_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo facturas para la empresa con ID: {empresa_id}", extra=request_info
    )
    facturas = get_documentos_by_empresa_id(db, empresa_id)
    if not facturas:
        logger.warning(
            f"No se encontraron facturas para la empresa con ID: {empresa_id}",
            extra=request_info,
        )
        raise HTTPException(
            status_code=404, detail="No se encontraron facturas para la empresa"
        )
    return facturas


@router.get("/cliente/{cliente_id}")
def get_facturas_by_cliente_id(
    cliente_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo facturas para el cliente con ID: {cliente_id}", extra=request_info
    )
    facturas = get_documentos_by_cliente_id(db, cliente_id)
    if not facturas:
        logger.warning(
            f"No se encontraron facturas para el cliente con ID: {cliente_id}",
            extra=request_info,
        )
        raise HTTPException(
            status_code=404, detail="No se encontraron facturas para el cliente"
        )
    return facturas


# Endnpoints para obtener IVA y operaciones asociadas a una factura
@router.get("/{factura_id}/iva")
def fetch_iva_by_factura_id(
    factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo IVA para la factura con ID: {factura_id}", extra=request_info
    )
    iva = get_iva_by_factura_id(db, factura_id)
    if not iva:
        logger.warning(
            f"IVA no encontrado para la factura con ID: {factura_id}",
            extra=request_info,
        )
        raise HTTPException(status_code=404, detail="IVA no encontrado para la factura")
    return iva


@router.get("/{factura_id}/detalles")
def fetch_detalles_factura_by_factura_id(
    factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo detalles de la factura con ID: {factura_id}", extra=request_info
    )
    detalles_factura = get_detalles_factura_by_factura_id(db, factura_id)
    if not detalles_factura:
        logger.warning(
            f"Detalles de factura no encontrados para la factura con ID: {factura_id}",
            extra=request_info,
        )
        raise HTTPException(
            status_code=404, detail="Detalles de factura no encontrados"
        )
    return detalles_factura


@router.get("/{factura_id}/pedido")
def fetch_pedido_by_factura_id(
    factura_id: int, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(
        f"Obteniendo pedido asociado a la factura con ID: {factura_id}",
        extra=request_info,
    )
    pedido = get_pedido_by_factura_id(db, factura_id)
    if not pedido:
        logger.warning(
            f"Pedido no encontrado para la factura con ID: {factura_id}",
            extra=request_info,
        )
        raise HTTPException(
            status_code=404, detail="Pedido no encontrado para la factura"
        )
    return pedido
