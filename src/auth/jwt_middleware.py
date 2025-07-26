import os
import requests
from jose import jwt, JWTError
import logging  # Add logging for debugging
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
        print("token:", token)
        print("Validando formato del token...")
        # Validar el formato del token
        if token.count(".") != 2:
            print("Error: El token no tiene el formato esperado (encabezado.payload.firma).")
            return None

        print("Obteniendo JWKS desde:", JWKS_URL)
        response = requests.get(JWKS_URL)
        if response.status_code != 200:
            print(f"Error al obtener el JWKS: {response.status_code}")
            return None

        jwks = response.json()
        print("JWKS obtenido:", jwks)
        # Validar la estructura del JWKS
        if not jwks or "keys" not in jwks or not jwks["keys"]:
            print("Error: JWKS no contiene claves válidas.")
            return None

        try:
            print("Extrayendo encabezado del token...")
            # Extraer el kid del encabezado del token
            unverified_header = jwt.get_unverified_header(token)
            print("Encabezado del token:", unverified_header)
            kid = unverified_header.get("kid")
            if not kid:
                print("Error: El token no contiene un 'kid' en el encabezado.")
                return None
        except Exception as e:
            print(f"Error al decodificar el encabezado del token: {str(e)}")
            return None

        print("Buscando clave correspondiente en el JWKS...")
        # Buscar la clave correspondiente en el JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            print("Error: No se encontró una clave coincidente en el JWKS.")
            return None

        try:
            print("Construyendo clave pública RSA...")
            # Convertir la clave JWK a formato PEM
            n = int.from_bytes(base64url_decode(key["n"].encode("utf-8")), "big")
            e = int.from_bytes(base64url_decode(key["e"].encode("utf-8")), "big")

            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())

            print("Decodificando el token...")
            # Decodificar el token utilizando la clave pública
            payload = jwt.decode(
                token, public_key, algorithms=["RS256"], options={"verify_aud": False}
            )
            print("Token decodificado exitosamente:", payload)
            return {"payload": payload}
        except ValueError as ve:
            print(f"Error al construir la clave pública: {str(ve)}")
            return None
        except JWTError as e:
            print(f"Error al decodificar el token: {str(e)}")
            return None
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return None
