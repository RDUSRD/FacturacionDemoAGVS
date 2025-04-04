"""
auth.py
This module handles authentication using OAuth2 with Authentik.

Features:
- OAuth2 login and callback endpoints.
- Logout functionality for both local and Authentik sessions.
- State management for OAuth2 flow.

Dependencies:
- fastapi: For API routing.
- core.oauth: For OAuth2 client integration.
- loggers.logger: For logging actions.
- secrets: For generating secure random states.
- os: For accessing environment variables.

Environment Variables:
- AUTHENTIK_REDIRECT_URI: Redirect URI for OAuth2.
- AUTHENTIK_LOGOUT_URL: Logout URL for Authentik.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
import secrets
import os
from core import oauth, templates
from loggers.logger import get_logger

# Crear una instancia del logger para el módulo de autenticación
logger = get_logger("AuthModule")

# Diccionario en memoria para almacenar los estados
app_state_store = {}


def get_request_info(request: Request):
    return {
        "device": getattr(request.state, "device", "UnknownDevice"),
        "ip": getattr(request.state, "ip", "UnknownIP"),
    }


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/oauth/authorize")
async def oauth_authorize(request: Request):
    redirect_uri = os.getenv("AUTHENTIK_REDIRECT_URI")

    # Generar un estado único y almacenarlo en la sesión
    state = secrets.token_urlsafe(16)  # Genera un estado único
    request.session["oauth_state"] = state  # Almacena el estado en la sesión

    # Redirigir al proveedor OAuth con el estado
    return await oauth.authentik.authorize_redirect(request, redirect_uri, state=state)


@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    device = getattr(request.state, "device", "UnknownDevice")
    ip = getattr(request.state, "ip", "UnknownIP")
    expected_state = request.session.get("oauth_state")
    received_state = request.query_params.get("state")
    if not expected_state or expected_state != received_state:
        logger.error(
            "State parameter mismatch in callback",
            extra={"device": device, "user": "Anonymous", "ip": ip},
        )
        raise HTTPException(status_code=400, detail="Mismatching state parameter.")
    request.session.pop("oauth_state", None)
    token_data = await oauth.authentik.authorize_access_token(request)
    access_token = token_data.get("access_token")
    if not access_token:
        logger.error(
            "No se recibió el access token",
            extra={"device": device, "user": "Anonymous", "ip": ip},
        )
        raise HTTPException(status_code=400, detail="No se recibió el access token")
    request.session["token"] = access_token
    logger.info(
        "Access token recibido y almacenado en sesión",
        extra={"device": device, "user": "AuthenticatedUser", "ip": ip},
    )
    return RedirectResponse(url="/dashboard")


@router.get("/logout")
async def logout(request: Request):
    request_info = get_request_info(request)
    request.session.clear()  # Limpiar la sesión del usuario
    # Eliminar la cookie de sesión para invalidar el token JWT
    response = RedirectResponse(url="/")
    logger.info("Cierre de sesión local", extra={**request_info, "user": "Anonymous"})
    return response


@router.get("/logout-authentik")
async def logout_authentik(request: Request):
    request_info = get_request_info(request)
    logger.info(
        "Cierre de sesión en Authentik", extra={**request_info, "user": "Anonymous"}
    )
    return RedirectResponse(url=os.getenv("AUTHENTIK_LOGOUT_URL"))
