from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from services import DocumentService
from jinja2 import Environment, FileSystemLoader
from loggers.logger import app_logger
from typing import Optional
import jwt
import time

def log_request_info(request: Request, action: str):
    ip = request.client.host
    device = request.headers.get("User-Agent", "UnknownDevice")
    app_logger.info(f"Acción: {action}", extra={"ip": ip, "device": device})

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
        decoded_token = jwt.decode(token, options={"verify_signature": False})
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

router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))

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

# Similar routes for debit_note_form, credit_note_form, delivery_order_form, retention_receipt_form, etc.
