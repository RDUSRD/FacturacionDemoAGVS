from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from src.documento.documentoService import (
    get_documento_by_id,
    get_all_documentos,
    get_documento_by_numero_control,
    get_documentos_by_empresa_id,
    get_documentos_by_cliente_id,
    get_or_create_factura,
)
from src.documento.factura.facturaSchema import FacturaSchema
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("DocumentoRouter")

router = APIRouter(prefix="/documento", tags=["Documento"])


# Endpoints para obtener documentos
@router.get("/")
def get_documentos(request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Obteniendo todos los documentos", extra=request_info)
    return get_all_documentos(db)


@router.get("/{documento_id}")
def get_documento(documento_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo documento con ID: {documento_id}", extra=request_info)
    documento = get_documento_by_id(db, documento_id)
    if not documento:
        logger.warning(f"Documento con ID: {documento_id} no encontrado", extra=request_info)
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


@router.get("/numero-control/{numero_control}")
def get_documento_numero_control(numero_control: str, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo documento con número de control: {numero_control}", extra=request_info)
    documento = get_documento_by_numero_control(db, numero_control)
    if not documento:
        logger.warning(f"Documento con número de control: {numero_control} no encontrado", extra=request_info)
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


@router.get("/empresa/{empresa_id}")
def get_documentos_empresa_id(empresa_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo documentos para la empresa con ID: {empresa_id}", extra=request_info)
    documentos = get_documentos_by_empresa_id(db, empresa_id)
    if not documentos:
        logger.warning(f"No se encontraron documentos para la empresa con ID: {empresa_id}", extra=request_info)
        raise HTTPException(
            status_code=404,
            detail="No se encontraron documentos para la empresa especificada",
        )
    return documentos


@router.get("/cliente/{cliente_id}")
def get_documentos_cliente_id(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo documentos para el cliente con ID: {cliente_id}", extra=request_info)
    documentos = get_documentos_by_cliente_id(db, cliente_id)
    if not documentos:
        logger.warning(f"No se encontraron documentos para el cliente con ID: {cliente_id}", extra=request_info)
        raise HTTPException(
            status_code=404,
            detail="No se encontraron documentos para el cliente especificado",
        )
    return documentos


# Endpoints para crear documentos
@router.post("/create/factura")
def create_factura_endpoint(factura_data: FacturaSchema, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Creando o obteniendo factura", extra=request_info)
    return get_or_create_factura(db, factura_data)
