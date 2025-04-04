"""
core.py
This module initializes the OAuth client for authentication using Authentik and sets up Jinja2 templates for rendering HTML.

Dependencies:
- os: For environment variable access.
- fastapi.templating.Jinja2Templates: For template rendering.
- authlib.integrations.starlette_client.OAuth: For OAuth client integration.
- dotenv.load_dotenv: For loading environment variables from a .env file.

Environment Variables:
- AUTHENTIK_URL: Base URL for Authentik.
- AUTHENTIK_CLIENT_ID: Client ID for Authentik.
- AUTHENTIK_CLIENT_SECRET: Client secret for Authentik.
- AUTHENTIK_REDIRECT_URI: Redirect URI for OAuth.
- AUTHENTIK_JWKS_URL: JWKS URL for Authentik.
"""

import os
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

url = os.getenv("AUTHENTIK_URL")
templates = Jinja2Templates(directory="templates")
oauth = OAuth()

oauth.register(
    name='authentik',
    client_id=os.getenv("AUTHENTIK_CLIENT_ID"),
    client_secret=os.getenv("AUTHENTIK_CLIENT_SECRET"),
    authorize_url=f'{url}/application/o/authorize/',
    access_token_url=f'{url}/application/o/token/',
    refresh_token_url=f'{url}/application/o/token/',
    redirect_uri=os.getenv("AUTHENTIK_REDIRECT_URI"),
    client_kwargs={'scope': 'openid profile email offline_access'},
    jwks_uri=os.getenv("AUTHENTIK_JWKS_URL")
)
