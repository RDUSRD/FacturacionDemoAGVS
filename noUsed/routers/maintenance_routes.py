from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from noUsed.schemasNoUsed import DefaultEmisorSchema
from services import DocumentService
from loggers.logger import app_logger
from jinja2 import Environment, FileSystemLoader

def log_request_info(request: Request, action: str):
    ip = request.client.host
    device = request.headers.get("User-Agent", "UnknownDevice")
    app_logger.info(f"Acción: {action}", extra={"ip": ip, "device": device})

router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))

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
