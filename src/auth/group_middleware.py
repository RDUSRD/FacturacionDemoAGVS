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
        ("/empresa", "ALL"): ["authentik Admins"],
        # Rutas para el módulo clientes
        ("/cliente", "ALL"): ["authentik Admins"],
        # Rutas para el módulo productos
        ("/producto", "ALL"): ["authentik Admins"],
        # Rutas para el módulo pedidos
        ("/pedido", "ALL"): ["authentik Admins"],
        # Rutas para el módulo documentos
        ("/documento", "ALL"): ["authentik Admins"],
        # Rutas para el módulo facturas
        ("/factura", "ALL"): ["authentik Admins"],
        # Rutas para el módulo detalle de facturas
        ("/detalle_factura", "ALL"): ["authentik Admins"],
        # Rutas para el módulo monedas
        ("/moneda", "ALL"): ["authentik Admins"],
        # Rutas para el módulo loggers
        ("/logger", "ALL"): ["authentik Admins"],
        # Rutas para el módulo autenticación
        ("/auth", "ALL"): ["authentik Admins"],
        # Rutas para notas
        ("/notas", "ALL"): ["authentik Admins"],
    }

    # Define excluded routes
    excluded_routes = [
        "/docs",
        "/openapi.json",
        "/oauth",
        "/get-token",
    ]

    async def dispatch(self, request: Request, call_next):
        try:
            # Log para depuración de rutas excluidas
            if any(
                request.scope["path"].startswith(prefix)
                for prefix in self.excluded_routes
            ):
                try:
                    return await call_next(request)
                except Exception as e:
                    logger.error(
                        f"Error en call_next durante la exclusión: {str(e)}",
                        exc_info=True,
                        extra=get_request_info(request),
                    )
                    return JSONResponse(
                        status_code=500,
                        content={
                            "detail": "Error interno del servidor durante la exclusión."
                        },
                    )

            authorization: str = request.headers.get("Authorization", "")
            if not authorization.startswith("Bearer "):
                logger.warning(
                    "Authorization inválido.",
                    extra=get_request_info(request),
                )
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization inválido."},
                )

            token = authorization.split(" ")[1]
            decoded_token = decode_access_token_with_jwks(token)
            if not decoded_token:
                logger.error(
                    "El token no pudo ser decodificado o es inválido.",
                    extra=get_request_info(request),
                )
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token inválido o expirado."},
                )

            payload = decoded_token
            groups = payload.get("groups", [])

            # Determine the required group for the current route and method
            route = request.url.path
            method = request.method

            # Buscar coincidencias exactas, rutas con parámetros dinámicos o prefijos generales
            required_group = self.route_group_mapping.get((route, method))
            if not required_group:
                for (pattern, m), group in self.route_group_mapping.items():
                    if (
                        (m == method or m == "ALL")
                        and (pattern.endswith("}") and route.startswith(pattern.rsplit("/", 1)[0])
                             or route.startswith(pattern))
                    ):
                        required_group = group
                        break

            # Verificar si el usuario pertenece a cualquiera de los grupos permitidos
            if required_group and not any(group in groups for group in required_group):
                logger.warning(
                    f"Usuario {payload.get('nickname', 'UnknownUser')} no tiene acceso a este recurso {route}.",
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
