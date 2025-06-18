from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from loggers.logger import app_logger
from jinja2 import Environment, FileSystemLoader
from routers.frontend_routes import enforce_login

def log_request_info(request: Request, action: str):
    ip = request.client.host
    device = request.headers.get("User-Agent", "UnknownDevice")
    app_logger.info(f"Acción: {action}", extra={"ip": ip, "device": device})

router = APIRouter()
env = Environment(loader=FileSystemLoader("templates"))

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
