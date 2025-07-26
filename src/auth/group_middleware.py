from fastapi import Request, HTTPException  # Import Request and HTTPException
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)  # Import BaseHTTPMiddleware from Starlette
from starlette.responses import (
    JSONResponse,
)  # Import JSONResponse for custom error handling
from src.auth.jwt_middleware import (
    decode_access_token_with_jwks,
)  # Import token decoder
from src.loggers.loggerService import (
    get_logger,
    get_request_info,
)  # Import logger and request info extractor

logger = get_logger("GroupMembershipMiddleware")


class GroupMembershipMiddleware(BaseHTTPMiddleware):
    # Define a mapping of routes and methods to required groups
    route_group_mapping = {
        # Rutas para el módulo empresa
        ("/empresa", "GET"): "authentik Admins",
        ("/empresa/{empresa_id}", "GET"): "authentik Admins",
        ("/empresa/create", "POST"): "authentik Admins",
        ("/empresa/{empresa_id}", "PUT"): "authentik Admins",
        # Rutas para el módulo clientes
        ("/clientes", "GET"): "authentik Users",
        ("/clientes/{cliente_id}", "GET"): "authentik Users",
        ("/clientes/create", "POST"): "authentik Users",
        ("/clientes/{cliente_id}", "PUT"): "authentik Users",
        # Rutas para el módulo productos
        ("/productos", "GET"): "authentik Managers",
        ("/productos/{producto_id}", "GET"): "authentik Managers",
        ("/productos/create", "POST"): "authentik Managers",
        ("/productos/{producto_id}", "PUT"): "authentik Managers",
    }

    # Define excluded routes
    excluded_routes = [
        "/docs",
        "/openapi.json",
        "/oauth",  # Excluir todas las rutas que comiencen con /oauth
        "/auth/get-token",
        "/auth/decode-token",
    ]

    async def dispatch(self, request: Request, call_next):
        try:
            # Log para depuración de rutas excluidas
            print(f"Ruta solicitada: {request.scope['path']}")
            if any(request.scope["path"].startswith(prefix) for prefix in self.excluded_routes):
                print(f"Ruta {request.scope['path']} excluida del middleware.")
                try:
                    return await call_next(request)
                except Exception as e:
                    logger.error(f"Error en call_next durante la exclusión: {str(e)}", exc_info=True)
                    return JSONResponse(
                        status_code=500,
                        content={"detail": "Error interno del servidor durante la exclusión."},
                    )

            authorization: str = request.headers.get("Authorization", "")
            if not authorization.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Encabezado Authorization inválido."},
                )

            token = authorization.split(" ")[1]
            print(f"Token: {token}")  # Debugging line to print the token
            decoded_token = decode_access_token_with_jwks(token)
            print(f"Decoded Token: {decoded_token}")
            if "error" in decoded_token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token inválido o expirado."},
                )

            payload = decoded_token.get("payload", {})
            groups = payload.get("groups", [])

            # Determine the required group for the current route and method
            route = request.url.path
            method = request.method
            required_group = self.route_group_mapping.get((route, method))

            if required_group and required_group not in groups:
                logger.warning(
                    f"Usuario {payload.get('nickname', 'UnknownUser')} no tiene acceso a este recurso.",
                    extra=get_request_info(request),
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "No tienes acceso a este recurso."},
                )

            # Attach payload to the request state for further use
            request.state.user_payload = payload
            return await call_next(request)

        except Exception as e:
            logger.error(
                f"Error en el middleware: {str(e)}", extra=get_request_info(request)
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Error interno del servidor en el middleware."},
            )
