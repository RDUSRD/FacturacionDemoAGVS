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

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2AuthorizationCodeBearer
import secrets
import os
from core import oauth, templates, url
from loggers.logger import get_logger

# Crear una instancia del logger para el módulo de autenticación
logger = get_logger("AuthModule")

# Diccionario en memoria para almacenar los estados
app_state_store = {}

# Define OAuth2 scheme for Authentik
authentik_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{url}/application/o/authorize/",
    tokenUrl=f"{url}/application/o/token/"
)


def get_request_info(request: Request):
    """
    Extracts device and IP information from the request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        dict: A dictionary containing device and IP information.
    """
    return {
        "device": getattr(request.state, "device", "UnknownDevice"),
        "ip": getattr(request.state, "ip", "UnknownIP"),
    }


router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def root(request: Request):
    """
    Serves the login page.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        HTMLResponse: The rendered login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/oauth/authorize", include_in_schema=False)
async def oauth_authorize(request: Request):
    """
    Initiates the OAuth2 authorization flow.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        RedirectResponse: Redirects to the OAuth2 provider.
    """
    redirect_uri = os.getenv("AUTHENTIK_REDIRECT_URI")

    # Generar un estado único y almacenarlo en la sesión
    state = secrets.token_urlsafe(16)  # Genera un estado único
    request.session["oauth_state"] = state  # Almacena el estado en la sesión

    # Redirigir al proveedor OAuth con el estado
    return await oauth.authentik.authorize_redirect(request, redirect_uri, state=state)


@router.get("/oauth/callback", include_in_schema=False)
async def oauth_callback(request: Request):
    """
    Handles the OAuth2 callback and retrieves the access token.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        RedirectResponse: Redirects to the /docs page.
    """
    device = getattr(request.state, "device", "UnknownDevice")
    ip = getattr(request.state, "ip", "UnknownIP")
    expected_state = request.cookies.get("oauth_state")
    received_state = request.query_params.get("state")

    if not expected_state or expected_state != received_state:
        logger.error(
            "State parameter mismatch in callback",
            extra={"device": device, "user": "Anonymous", "ip": ip},
        )
        raise HTTPException(status_code=400, detail="Mismatching state parameter.")

    # Clear the state cookie
    response = RedirectResponse(url="/docs")
    response.delete_cookie("oauth_state")

    # Retrieve the access token using the code
    try:
        token_data = await oauth.authentik.authorize_access_token(request)
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError("No se recibió el access token")

        # Store the token in a cookie
        response.set_cookie(key="token", value=access_token, httponly=True)

        logger.info(
            "Access token recibido y almacenado en cookie",
            extra={"device": device, "user": "AuthenticatedUser", "ip": ip},
        )
    except Exception as e:
        logger.error(
            f"Error al obtener el access token: {e}",
            extra={"device": device, "user": "Anonymous", "ip": ip},
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
    request_info = get_request_info(request)
    request.session.clear()  # Limpiar la sesión del usuario
    # Eliminar la cookie de sesión para invalidar el token JWT
    response = RedirectResponse(url="/")
    logger.info("Cierre de sesión local", extra={**request_info, "user": "Anonymous"})
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
    request_info = get_request_info(request)
    logger.info(
        "Cierre de sesión en Authentik", extra={**request_info, "user": "Anonymous"}
    )
    return RedirectResponse(url=os.getenv("AUTHENTIK_LOGOUT_URL"))


@router.get("/docs", include_in_schema=False)
def protected_swagger_ui(request: Request, token: str = Depends(authentik_oauth2_scheme)):
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
