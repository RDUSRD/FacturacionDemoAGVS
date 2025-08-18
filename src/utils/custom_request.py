import requests


def obtener_precio_bcv():
    try:
        # URL de la API para obtener el precio del dólar oficial
        url = "https://ve.dolarapi.com/v1/dolares/oficial"

        # Realizar la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa

        # Parsear la respuesta JSON
        data = response.json()

        # Obtener el promedio y la fecha de actualización
        promedio = round(data["promedio"], 4)  # Redondear a 4 decimales
        fecha_actualizacion = data["fechaActualizacion"]

        # Imprimir la fecha de actualización
        print(f"Fecha de actualización: {fecha_actualizacion}")

        return promedio
    except Exception as e:
        print(f"Error al obtener el precio del BCV: {e}")
        return None


# Ejemplo de uso
precio_bcv = obtener_precio_bcv()
if precio_bcv:
    print(f"El precio del dólar según el BCV es: {precio_bcv}")