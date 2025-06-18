from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from noUsed.schemasNoUsed import (
    FacturaCreate,
    DebitNoteCreate,
    CreditNoteCreate,
    DeliveryOrderCreate,
    RetentionReceiptCreate,
    DocumentResponse,
)
from services import DocumentService
from loggers.logger import app_logger

def log_request_info(request: Request, action: str):
    ip = request.client.host
    device = request.headers.get("User-Agent", "UnknownDevice")
    app_logger.info(f"Acción: {action}", extra={"ip": ip, "device": device})

router = APIRouter()

@router.post("/facturas/", response_model=DocumentResponse)
def create_factura(
    request: Request, factura: FacturaCreate, db: Session = Depends(get_db)
):
    try:
        log_request_info(request, "Creando factura")
        result = DocumentService.create_factura(db, factura, request.client.host)
        return result
    except Exception as e:
        app_logger.error(f"Error al crear factura: {e}")
        raise

@router.post("/debit_notes/", response_model=DocumentResponse)
def create_debit_note(
    request: Request, debit_note: DebitNoteCreate, db: Session = Depends(get_db)
):
    try:
        log_request_info(request, "Creando nota de débito")
        result = DocumentService.create_debit_note(db, debit_note, request.client.host)
        return result
    except Exception as e:
        app_logger.error(f"Error al crear nota de débito: {e}")
        raise

@router.post("/credit_notes/", response_model=DocumentResponse)
def create_credit_note(
    request: Request, credit_note: CreditNoteCreate, db: Session = Depends(get_db)
):
    try:
        log_request_info(request, "Creando nota de crédito")
        result = DocumentService.create_credit_note(
            db, credit_note, request.client.host
        )
        return result
    except Exception as e:
        app_logger.error(f"Error al crear nota de crédito: {e}")
        raise

@router.post("/delivery_orders/", response_model=DocumentResponse)
def create_delivery_order(
    request: Request, delivery_order: DeliveryOrderCreate, db: Session = Depends(get_db)
):
    try:
        log_request_info(request, "Creando orden de entrega")
        result = DocumentService.create_delivery_order(
            db, delivery_order, request.client.host
        )
        return result
    except Exception as e:
        app_logger.error(f"Error al crear orden de entrega: {e}")
        raise

@router.post("/retention_receipts/", response_model=DocumentResponse)
def create_retention_receipt(
    request: Request,
    retention_receipt: RetentionReceiptCreate,
    db: Session = Depends(get_db),
):
    try:
        log_request_info(request, "Creando comprobante de retención")
        result = DocumentService.create_retention_receipt(
            db, retention_receipt, request.client.host
        )
        return result
    except Exception as e:
        app_logger.error(f"Error al crear comprobante de retención: {e}")
        raise
