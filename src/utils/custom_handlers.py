from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import os
import secrets
from core import oauth

async def authentik_swagger_protection(request: Request, call_next):
    """
    Middleware to protect Swagger documentation.
    Redirects to Authentik for authentication using the registered OAuth client.
    """
    if request.url.path == "/docs":
        token = request.cookies.get("token")
        if not token:
            logging.info("No token found in cookies. Redirecting to Authentik.")
            redirect_uri = os.getenv("AUTHENTIK_REDIRECT_URI")

            # Generate a unique state
            state = secrets.token_urlsafe(16)

            # Redirect to the OAuth provider with the state
            response = await oauth.authentik.authorize_redirect(
                request, redirect_uri, state=state
            )

            # Store the state in a cookie
            response.set_cookie(key="oauth_state", value=state, httponly=True)

            return response

    response = await call_next(request)
    return response


async def custom_404_handler(request: Request, exc):
    """
    Custom handler for 404 errors.
    """
    return JSONResponse(
        status_code=404,
        content={"message": "La ruta que intentas acceder no existe. Por favor verifica la URL."},
    )
