"""
main.py
This is the entry point for the FastAPI application. It sets up middleware, routes, and database initialization.

Features:
- Middleware for session management and caching.
- OAuth2 integration for authentication.
- Static and template file serving.
- Database initialization with default data.

Dependencies:
- fastapi: For building the web application.
- sqlalchemy: For database interaction.
- jinja2: For template rendering.
- dotenv: For environment variable management.
- authlib: For OAuth2 client integration.

Environment Variables:
- SESSION_SECRET_KEY: Secret key for session management.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from database import Base, engine, get_db
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from models import DigitalPrinter
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from routers.routes import router
from loggers.logger import app_logger  # Importar el logger global
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from routers.auth import router as auth_router


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    printer = db.query(DigitalPrinter).first()
    if not printer:
        printer = DigitalPrinter(
            name="Imprenta Digital Ejemplo",
            rif="J-12345678-9",
            control_number_start=1,
            control_number_end=1000,
            current_control_number=0,
            authorization_nomenclature="PA-2025-001",
            authorization_date=datetime.now(),
        )
        db.add(printer)
        db.commit()
    yield

# Load environment variables
load_dotenv()

# Initialize OAuth client
oauth = OAuth()
url = os.getenv("AUTHENTIK_URL")
oauth.register(
    name='authentikk',
    client_id=os.getenv("AUTHENTIK_CLIENT_ID"),
    client_secret=os.getenv("AUTHENTIK_CLIENT_SECRET"),
    authorize_url=f'{url}/application/o/authorize/',
    access_token_url=f'{url}/application/o/token/',
    refresh_token_url=f'{url}/application/o/token/',
    redirect_uri=os.getenv("AUTHENTIK_REDIRECT_URI"),
    client_kwargs={'scope': 'openid profile email offline_access'},
    jwks_uri=os.getenv("AUTHENTIK_JWKS_URL")
)

# Add session middleware for OAuth2
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f'{url}/application/o/authorize/',
    tokenUrl=f'{url}/application/o/token/',
)

app = FastAPI(lifespan=lifespan)
app.add_middleware(NoCacheMiddleware)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),
    session_cookie="session",
    max_age=3600,  # Tiempo de vida de la sesión (1 hora)
    same_site="lax"
)
app.mount("/documents", StaticFiles(directory="documents"), name="documents")
app.mount(
    "/static",
    StaticFiles(directory="static", html=True, check_dir=False),
    name="static",
)
app.include_router(router)
app.include_router(auth_router)

env = Environment(loader=FileSystemLoader("templates"))
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

# Registrar un log al iniciar la aplicación
app_logger.info("Aplicación FastAPI iniciada correctamente")

