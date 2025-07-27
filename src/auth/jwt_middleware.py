import os
import requests
from jose import jwt, JWTError
from jose.utils import base64url_decode
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# URL del JWKS para Authentik
JWKS_URL = os.getenv("AUTHENTIK_JWKS_URL")


def decode_access_token_with_jwks(token: str):
    """
    Decodifica un access_token utilizando el JWKS.

    Args:
        token (str): El token JWT a decodificar.

    Returns:
        dict: Un diccionario con los datos decodificados o None si ocurre un error.
    """
    try:
        # Validar el formato del token
        if token.count(".") != 2:
            return None

        response = requests.get(JWKS_URL)
        if response.status_code != 200:
            return None

        jwks = response.json()
        # Validar la estructura del JWKS
        if not jwks or "keys" not in jwks or not jwks["keys"]:
            return None

        try:
            # Extraer el kid del encabezado del token
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                return None
        except Exception:
            return None

        # Buscar la clave correspondiente en el JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            return None

        try:
            # Convertir la clave JWK a formato PEM
            n = int.from_bytes(base64url_decode(key["n"].encode("utf-8")), "big")
            e = int.from_bytes(base64url_decode(key["e"].encode("utf-8")), "big")

            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())

            # Decodificar el token utilizando la clave pública
            payload = jwt.decode(
                token, public_key, algorithms=["RS256"], options={"verify_aud": False}
            )
            return payload
        except ValueError:
            return None
        except JWTError:
            return None
    except Exception:
        return None
