"""
routes.py
This module defines the API routes for the application, including endpoints for creating and managing documents.

Features:
- CRUD operations for documents (facturas, debit notes, credit notes, etc.).
- Middleware for JWT validation and user authentication.
- Frontend routes for rendering HTML templates.

Dependencies:
- fastapi: For API routing.
- sqlalchemy: For database interaction.
- jinja2: For template rendering.
- loggers.logger: For logging actions.
- jwt: For JSON Web Token handling.

Functions:
- create_factura, create_debit_note, create_credit_note, etc.: API endpoints for document creation.
- enforce_login: Middleware for enforcing user login.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    FacturaCreate,
    DebitNoteCreate,
    CreditNoteCreate,
    DeliveryOrderCreate,
    RetentionReceiptCreate,
    DocumentResponse,
    DefaultEmisorSchema,
)
from services import DocumentService
from models import Document, Receptor, AuditLog
from jinja2 import Environment, FileSystemLoader
from typing import Optional
from loggers.logger import app_logger
import jwt
import time


router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))


def log_request_info(request: Request, action: str):
    ip = request.client.host
    device = request.headers.get("User-Agent", "UnknownDevice")
    app_logger.info(f"Acción: {action}", extra={"ip": ip, "device": device})


# Middleware to handle JWT and user attributes
async def enforce_login(request: Request):
    token = request.session.get("token")
    if not token:
        app_logger.warning(
            "No se encontró token en la sesión, redirigiendo a login",
            extra={
                "device": request.headers.get("User-Agent", "UnknownDevice"),
                "ip": request.client.host,
            },
        )
        return None, RedirectResponse(url="/")

    try:
        # Decodificar el token sin verificar la firma para inspeccionar el contenido
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Verificar si el token ha expirado
        if int(time.time()) >= decoded_token.get("exp", 0):
            app_logger.info(
                "El token ha expirado, limpiando sesión y redirigiendo a login",
                extra={
                    "device": request.headers.get("User-Agent", "UnknownDevice"),
                    "ip": request.client.host,
                },
            )
            request.session.clear()
            return None, RedirectResponse(url="/")

        # Si el token es válido, devolver la información del usuario
        return decoded_token, None
    except jwt.ExpiredSignatureError:
        app_logger.error(
            "El token ha expirado",
            extra={
                "device": request.headers.get("User-Agent", "UnknownDevice"),
                "ip": request.client.host,
            },
        )
        request.session.clear()
        return None, RedirectResponse(url="/")
    except jwt.InvalidTokenError as e:
        app_logger.error(
            f"Error al decodificar el token: {e}",
            extra={
                "device": request.headers.get("User-Agent", "UnknownDevice"),
                "ip": request.client.host,
            },
        )
        request.session.clear()
        return None, RedirectResponse(url="/")


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


# Rutas de frontend
@router.get("/dashboard", response_class=HTMLResponse)
async def menu(request: Request):
    log_request_info(request, "Accediendo al menú principal")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al menú principal",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    template = env.get_template("dashboard.html")
    return template.render(user_info=user_info)


@router.get("/factura", response_class=HTMLResponse)
async def factura_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de factura")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de factura",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("factura.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.get("/debit_note", response_class=HTMLResponse)
async def debit_note_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de nota de débito")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de nota de débito",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("debit_note.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.get("/credit_note", response_class=HTMLResponse)
async def credit_note_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de nota de crédito")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de nota de crédito",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("credit_note.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.get("/delivery_order", response_class=HTMLResponse)
async def delivery_order_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de orden de entrega")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de orden de entrega",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("delivery_order.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.get("/retention_receipt", response_class=HTMLResponse)
async def retention_receipt_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de comprobante de retención")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de comprobante de retención",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("retention_receipt.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.get("/documents", response_class=HTMLResponse)
async def get_documents(
    request: Request,
    document_type: Optional[str] = None,
    document_number: Optional[str] = None,
    receptor_rif: Optional[str] = None,
    db: Session = Depends(get_db),
):
    log_request_info(request, "Consultando documentos")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido a la consulta de documentos",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    try:
        if document_type == "":
            document_type = None
        if receptor_rif == "":
            receptor_rif = None

        document_number_int = None
        if document_number and document_number.strip():
            try:
                document_number_int = int(document_number)
            except ValueError:
                app_logger.warning("Número de documento inválido")

        query = db.query(Document)
        if document_type:
            query = query.filter(Document.document_type == document_type)
        if document_number_int is not None:
            query = query.filter(Document.document_number == document_number_int)
        if receptor_rif:
            query = query.join(Document.receptor).filter(Receptor.rif == receptor_rif)

        documents = query.all()
        app_logger.info(f"Se encontraron {len(documents)} documentos")
        template = env.get_template("documents.html")
        return template.render(documents=documents, user_info=user_info)
    except Exception as e:
        app_logger.error(f"Error al consultar documentos: {e}")
        raise


@router.get("/maintenance", response_class=HTMLResponse)
async def maintenance_form(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Accediendo al formulario de mantenimiento")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido al formulario de mantenimiento",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("maintenance.html")
    return template.render(default_emisor=default_emisor, user_info=user_info)


@router.post("/maintenance/update_emisor", response_class=HTMLResponse)
async def update_default_emisor(
    request: Request, emisor: DefaultEmisorSchema, db: Session = Depends(get_db)
):
    log_request_info(request, "Actualizando datos del emisor")
    try:
        DocumentService.update_default_emisor(db, emisor)
        default_emisor = DocumentService.get_default_emisor(db)
        app_logger.info("Datos del emisor actualizados con éxito")
        template = env.get_template("maintenance.html")
        return template.render(
            default_emisor=default_emisor,
            message="Datos del emisor actualizados con éxito",
        )
    except Exception as e:
        app_logger.error(f"Error al actualizar datos del emisor: {e}")
        raise


@router.get("/audit_logs", response_class=HTMLResponse)
async def get_audit_logs(request: Request, db: Session = Depends(get_db)):
    log_request_info(request, "Consultando registros de auditoría")
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido a los registros de auditoría",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )
    try:
        audit_logs = db.query(AuditLog).order_by(AuditLog.transaction_date.desc()).all()
        app_logger.info(f"Se encontraron {len(audit_logs)} registros de auditoría")
        template = env.get_template("audit_logs.html")
        return template.render(audit_logs=audit_logs, user_info=user_info)
    except Exception as e:
        app_logger.error(f"Error al consultar registros de auditoría: {e}")
        raise


@router.get("/secure-documents", response_class=HTMLResponse)
async def secure_documents(request: Request, db: Session = Depends(get_db)):
    user_info, redirect = await enforce_login(request)
    if redirect:
        return redirect

    app_logger.info(
        "Acceso permitido a documentos seguros",
        extra={
            "device": request.headers.get("User-Agent", "UnknownDevice"),
            "user": user_info.get("preferred_username", "UnknownUser"),
            "ip": request.client.host,
        },
    )

    documents = db.query(Document).all()
    template = env.get_template("documents.html")
    return template.render(documents=documents, user_info=user_info)
