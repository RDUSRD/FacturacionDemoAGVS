"""
main.py
Este archivo es el punto de entrada para la aplicación FastAPI. Configura middleware, rutas y la inicialización de la base de datos.

Características:
- Configuración de middleware para servir archivos estáticos.
- Registro de rutas para diferentes módulos de la aplicación.
- Inicialización de la base de datos.

Dependencias:
- fastapi: Framework para construir la aplicación web.
- sqlalchemy: ORM para interacción con la base de datos.
- dotenv: Para cargar variables de entorno desde un archivo .env.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from loggers.logger import app_logger
from dotenv import load_dotenv
from fastapi.security import OAuth2AuthorizationCodeBearer
from core import url, oauth
import os
from starlette.middleware.sessions import SessionMiddleware
import secrets
import logging

# Importar routers
from src.empresa.empresaRouter import router as empresa_router
from src.cliente.clienteRouter import router as cliente_router
from src.documento.documentoRouter import router as documento_router
from src.documento.factura.facturaRouter import router as factura_router
from src.documento.notas.notaRouter import router as nota_router
from src.documento.orden_entrega.ordenEntregaRouter import (
    router as orden_entrega_router,
)
from src.comprobante_retencion.comprobanteRetencionRouter import (
    router as comprobante_retencion_router,
)
from src.producto.productoRouter import router as producto_router
from src.detalleFactura.detalleFacturaRouter import router as detalle_factura_router
from src.auditoria.audRouter import router as auditoria_router
from src.auth.auth_routes import router as auth_router

# Cargar variables de entorno
load_dotenv()

# Define OAuth2 scheme for Authentik
authentik_oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{url}/application/o/authorize/",
    tokenUrl=f"{url}/application/o/token/",
)


async def lifespan_with_reset(app: FastAPI):
    """
    Resets the database by dropping and recreating all tables during application startup.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    print("Reiniciando la base de datos...")
    Base.metadata.drop_all(bind=engine)
    print("Tablas eliminadas correctamente.")
    Base.metadata.create_all(bind=engine)
    print("Tablas recreadas correctamente.")
    yield


async def lifespan_without_reset(app: FastAPI):
    """
    Starts the application without resetting the database.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    print("Iniciando la aplicación sin reiniciar la base de datos...")
    yield


# Configurar la aplicación FastAPI
USE_RESET = (
    False  # Cambiar a True para reiniciar la base de datos al iniciar la aplicación
)

app = FastAPI(
    description="API para la gestión de documentos y facturación",
    title="API Facturacion AGV Services",
    version="1.0.0",
    lifespan=lifespan_with_reset if USE_RESET else lifespan_without_reset,
)

# Middleware para servir archivos estáticos
app.mount("/documents", StaticFiles(directory="documents"), name="documents")
app.mount(
    "/static",
    StaticFiles(directory="static", html=True, check_dir=False),
    name="static",
)

# Middleware para manejar sesiones
@app.middleware("http")
async def authentik_swagger_protection(request: Request, call_next):
    """
    Middleware to protect Swagger documentation.
    Redirects to Authentik for authentication using the registered OAuth client.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or endpoint to call.

    Returns:
        Response: The HTTP response.
    """
    if request.url.path == "/docs":
        token = request.cookies.get("token")
        if not token:
            logging.info("No token found in cookies. Redirecting to Authentik.")
            redirect_uri = os.getenv("AUTHENTIK_REDIRECT_URI")

            # Generar un estado único
            state = secrets.token_urlsafe(16)

            # Redirigir al proveedor OAuth con el estado
            response = await oauth.authentik.authorize_redirect(request, redirect_uri, state=state)

            # Almacenar el estado en una cookie
            response.set_cookie(key="oauth_state", value=state, httponly=True)

            return response

    response = await call_next(request)
    return response


# Incluir routers con tags para organización
app.include_router(empresa_router)
app.include_router(cliente_router)
app.include_router(documento_router)
app.include_router(factura_router)
app.include_router(nota_router)
app.include_router(orden_entrega_router)
app.include_router(comprobante_retencion_router)
app.include_router(producto_router)
app.include_router(detalle_factura_router)
app.include_router(auditoria_router)
app.include_router(auth_router)

# Registrar un log al iniciar la aplicación
app_logger.info("Aplicación FastAPI iniciada correctamente")

# Agregar el SessionMiddleware
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret_key")
)
