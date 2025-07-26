import os
import secrets
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from src.loggers.loggerService import get_request_info, get_logger
from core import oauth

# Crear una instancia del logger para el servicio de autenticación
logger = get_logger("AuthService")

def get_access_token(request: Request):
    """
    Obtiene el token de acceso desde las cookies.

    Args:
        request (Request): La solicitud HTTP entrante.

    Returns:
        JSONResponse: El token de acceso o un error si no se encuentra.
    """
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="No se encontró el token de acceso.")

    logger.info("Token de acceso obtenido", extra=get_request_info(request))
    return JSONResponse(content={"access_token": token})
