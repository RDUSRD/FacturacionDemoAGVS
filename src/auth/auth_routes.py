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
- jose: For JWT decoding.

Environment Variables:
- AUTHENTIK_REDIRECT_URI: Redirect URI for OAuth2.
- AUTHENTIK_LOGOUT_URL: Logout URL for Authentik.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2AuthorizationCodeBearer
import os
import secrets
import asyncio
from core import url, oauth
from src.loggers.loggerService import get_logger, get_request_info
from src.auth.auth_service import (
    get_access_token,
)
from src.auth.jwt_middleware import decode_access_token_with_jwks

# Crear una instancia del logger para el módulo de autenticación
logger = get_logger("AuthModule")

# Diccionario en memoria para almacenar los estados
app_state_store = {}

# Define OAuth2 scheme for Authentik
authentik_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{url}/application/o/authorize/",
    tokenUrl=f"{url}/application/o/token/",
)

# JWKS URL for Authentik
JWKS_URL = os.getenv("AUTHENTIK_JWKS_URL")  # Cambia esto por la URL de tu JWKS

router = APIRouter()


@router.get("/oauth/authorize", include_in_schema=False)
async def oauth_authorize(request: Request):
    """
    Inicia el flujo de autorización OAuth2.

    Args:
        request (Request): La solicitud HTTP entrante.

    Returns:
        RedirectResponse: Redirección al proveedor OAuth2.
    """
    redirect_uri = os.getenv("AUTHENTIK_REDIRECT_URI")
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state

    logger.info("Inicio del flujo de autorización OAuth2", extra=get_request_info(request))
    return oauth.authentik.authorize_redirect(request, redirect_uri, state=state)


@router.get("/oauth/callback", include_in_schema=False)
async def oauth_callback(request: Request):
    """
    Maneja el callback de OAuth2 y recupera el token de acceso.

    Args:
        request (Request): La solicitud HTTP entrante.

    Returns:
        RedirectResponse: Redirección a la página de documentación.
    """
    expected_state = request.cookies.get("oauth_state")
    received_state = request.query_params.get("state")

    if not expected_state or expected_state != received_state:
        logger.error(
            "State parameter mismatch en callback", extra=get_request_info(request)
        )
        raise HTTPException(status_code=400, detail="Mismatching state parameter.")

    response = RedirectResponse(url="/docs")
    response.delete_cookie("oauth_state")
    print(
        f"State eliminado de la cookie: {expected_state}"
    )  # Reemplazo de log con print

    try:
        print("Iniciando el flujo de autorización OAuth2...")
        token_data = await oauth.authentik.authorize_access_token(request)
        print(f"Tipo de token_data: {type(token_data)}")

        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError("No se recibió el access token")

        response.set_cookie(key="token", value=access_token, httponly=True)
        logger.info(
            "Access token recibido y almacenado en cookie",
            extra=get_request_info(request),
        )
    except Exception as e:
        logger.error(
            f"Error al obtener el access token: {e}", extra=get_request_info(request)
        )
        raise HTTPException(status_code=400, detail="Error al obtener el access token")

    return response


@router.get("/logout", include_in_schema=False)
async def logout(request: Request):
    """
    Logs out the user locally by clearing the session.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        RedirectResponse: Redirects to the root page.
    """
    request.session.clear()  # Limpiar la sesión del usuario
    # Eliminar la cookie de sesión para invalidar el token JWT
    response = RedirectResponse(url="/")
    logger.info("Cierre de sesión local", extra=get_request_info(request))
    return response


@router.get("/logout-authentik", include_in_schema=False)
async def logout_authentik(request: Request):
    """
    Logs out the user from Authentik.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        RedirectResponse: Redirects to the Authentik logout URL.
    """
    logger.info("Cierre de sesión en Authentik", extra=get_request_info(request))
    return RedirectResponse(url=os.getenv("AUTHENTIK_LOGOUT_URL"))


@router.get("/docs", include_in_schema=False)
def protected_swagger_ui(
    request: Request, token: str = Depends(authentik_oauth2_scheme)
):
    """
    Protects the Swagger documentation with Authentik authentication.

    Args:
        request (Request): The incoming HTTP request.
        token (str): The OAuth2 token for authentication.

    Returns:
        HTMLResponse: The Swagger UI page.
    """
    app = request.app
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title)


# Ruta para poder obtener el token de acceso desde el frontend
@router.get("/get-token", include_in_schema=True)
async def get_token(request: Request):
    return get_access_token(request)


@router.get("/decode-token", include_in_schema=True)
async def decode_token(token: str):
    return decode_access_token_with_jwks(token)
