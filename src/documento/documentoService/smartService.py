# Función para generar el JSON para la API de imprenta digital
import os
import requests
from src.cliente.clienteSchema import ClienteSchema
from src.documento.factura.facModel import Factura
from src.documento.factura.iva.ivaModel import iva
from src.empresa.empresaSchema import EmpresaSchema

SEND_EMAIL_SMART = os.getenv("SEND_EMAIL_SMART")

if SEND_EMAIL_SMART is None:
    exception = ValueError(
        "La variable de entorno SEND_EMAIL_SMART no está configurada."
    )
    raise exception


def to_float(name, value):  # Convertir a float y manejar excepciones
    try:
        # print(f"Convirtiendo a float {name}: {value} ({type(value)})")
        return float(value)
    except (ValueError, TypeError) as e:
        print(f"Error al convertir a float {name}: {value} ({type(value)}) - {e}")
        return 0.0


def generar_json_imprenta(
    factura: Factura,
    detalles,
    cliente: ClienteSchema,
    empresa: EmpresaSchema,
    impuestos: iva,
    precio_bcv: float,
    tipo_documento: int,
    pedido_id: int,
):
    # Convertir a minúsculas para evitar problemas de escritura
    tipo_documento_lower = factura.tipo_documento.lower()
    tipo_cedula_lower = cliente.tipo_documento.lower()

    # Asignar el tipo de documento
    if tipo_documento_lower == "factura":
        idtipodocumento = 1
    elif tipo_documento_lower == "notadebito":
        idtipodocumento = 2
    elif tipo_documento_lower == "notacredito":
        idtipodocumento = 3
    elif tipo_documento_lower == "ordenentrega":
        idtipodocumento = 4
    elif tipo_documento_lower == "guiadespacho":
        idtipodocumento = 5
    else:
        raise ValueError(f"Tipo de documento desconocido: {factura.tipo_documento}")

    # Asignar el tipo de cédula del cliente
    if tipo_cedula_lower == "cedula":
        idtipocedulacliente = 1
    elif tipo_cedula_lower == "pasaporte":
        idtipocedulacliente = 2
    elif tipo_cedula_lower == "rif":
        idtipocedulacliente = 3
    else:
        raise ValueError(
            f"Tipo de cédula del cliente desconocido: {cliente.tipo_documento}"
        )

    json_data = {
        "rif": empresa.rif,
        "trackingid": pedido_id,
        "nombrecliente": cliente.nombre,
        "rifcedulacliente": cliente.documento,
        "emailcliente": cliente.email,
        "telefonocliente": cliente.telefono,
        "idtipocedulacliente": idtipocedulacliente,
        "idtipodocumento": idtipodocumento,
        "direccioncliente": cliente.domicilio_fiscal,
        "subtotal": to_float("subtotal", impuestos.subtotal_sin_descuento),
        "exento": to_float("exento", impuestos.monto_exento),
        "tasag": to_float("tasag", impuestos.iva_general),
        "baseg": to_float("baseg", impuestos.monto_base_general),
        "impuestog": to_float("impuestog", impuestos.iva_general_monto),
        "tasar": to_float("tasar", impuestos.iva_reducida),
        "baser": to_float("baser", impuestos.monto_base_reducida),
        "impuestor": to_float("impuestor", impuestos.iva_reducida_monto),
        "tasaa": to_float("tasaa", impuestos.iva_adicional),
        "basea": to_float("basea", impuestos.monto_base_adicional),
        "impuestoa": to_float("impuestoa", impuestos.iva_adicional_monto),
        "tasaigtf": to_float("tasaigtf", impuestos.igtf),
        "baseigtf": to_float("baseigtf", impuestos.base_igtf),
        "impuestoigtf": to_float("impuestoigtf", impuestos.monto_igtf),
        "total": to_float("total", impuestos.monto),
        "sendmail": "1" if SEND_EMAIL_SMART else "0",
        "relacionado": "",
        "sucursal": "",
        "numerointerno": factura.factura_id,
        "tasacambio": to_float("tasacambio", precio_bcv),
        "Observacion": "Factura generada automáticamente.",
        "cuerpofactura": [
            {
                "codigo": detalle.producto_id,
                "descripcion": detalle.producto.descripcion,
                "comentario": "",
                "precio": to_float("precio", detalle.precio_unitario),
                "cantidad": to_float("cantidad", detalle.cantidad),
                "tasa": to_float("tasa", detalle.producto.alicuota_iva),
                "impuesto": (
                    to_float(
                        "impuesto", detalle.total * detalle.producto.alicuota_iva / 100
                    )
                    if not detalle.producto.exento
                    else 0
                ),
                "descuento": to_float("descuento", detalle.descuento),
                "exento": detalle.producto.exento,
                "monto": to_float("monto", detalle.total),
            }
            for detalle in detalles
        ],
        "formasdepago": "",
    }
    return json_data


def enviar_a_imprenta(json_data: dict, url: str):
    print(f"Enviando a la URL: {url}")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('SMART_API_TOKEN')}",
        }
        # Agregar un tiempo de espera de 10 segundos
        print(f"Datos JSON a enviar: {json_data}")
        response = requests.post(url, json=json_data, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es 2xx
        return response.json()
    except requests.exceptions.Timeout:
        return {
            "error": "La solicitud a la API de imprenta excedió el tiempo de espera."
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
