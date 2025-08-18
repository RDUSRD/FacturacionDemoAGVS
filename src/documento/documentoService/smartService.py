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


def generar_json_imprenta(
    factura: Factura,
    detalles,
    cliente: ClienteSchema,
    empresa: EmpresaSchema,
    impuestos: iva,
    precio_bcv: float,
    tipo_documento: int,
):
    json_data = {
        "rif": empresa.rif,
        "trackingid": "0",
        "nombrecliente": cliente.nombre,
        "rifcedulacliente": cliente.documento,
        "emailcliente": cliente.email,
        "telefonocliente": cliente.telefono,
        "idtipocedulacliente": cliente.tipo_documento,  # 1: V, 2: E, ajusta según sea necesario
        "idtipodocumento": tipo_documento,  # 1: Factura, ajusta según el tipo de documento
        "direccioncliente": cliente.domicilio_fiscal,
        "subtotal": factura.subtotal,
        "exento": factura.monto_exento,
        "tasag": impuestos.iva_general,  # Tasa general (16%)
        "baseg": impuestos.monto_base_general,  # Base para alícuota general
        "impuestog": impuestos.iva_general_monto,  # IVA calculado para alícuota general
        "tasar": impuestos.iva_reducida,  # Tasa reducida (8%)
        "baser": impuestos.monto_base_reducida,  # Base para alícuota reducida
        "impuestor": impuestos.iva_reducida_monto,  # IVA calculado para alícuota reducida
        "tasaa": impuestos.iva_adicional,  # Tasa adicional (15%)
        "basea": impuestos.monto_base_adicional,  # Base para alícuota adicional
        "impuestoa": impuestos.iva_adicional_monto,  # IVA calculado para alícuota adicional
        "tasaigtf": 3,  # Tasa IGTF
        "baseigtf": (
            factura.monto_base + factura.monto_exento if factura.aplica_igtf else 0
        ),
        "impuestoigtf": factura.monto_igtf,
        "total": factura.total,
        "sendmail": "1" if SEND_EMAIL_SMART else "0",  # Enviar correo al cliente
        "relacionado": "",  # Número de control relacionado (si aplica)
        "sucursal": "",
        "numerointerno": factura.factura_id,
        "tasacambio": precio_bcv,
        "Observacion": "Factura generada automáticamente.",
        "cuerpofactura": [
            {
                "codigo": detalle.producto_id,
                "descripcion": detalle.producto.nombre,
                "comentario": "",
                "precio": detalle.precio_unitario,
                "cantidad": detalle.cantidad,
                "tasa": 16 if not detalle.producto.exento else 0,
                "impuesto": detalle.total * 0.16 if not detalle.producto.exento else 0,
                "descuento": detalle.descuento,
                "exento": detalle.producto.exento,
                "monto": detalle.total,
            }
            for detalle in detalles
        ],
        "formasdepago": "",  # Agrega formas de pago si aplica
    }
    return json_data


# Función para enviar el JSON a la API de imprenta digital
def enviar_a_imprenta(json_data: dict, url: str):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=json_data, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es 2xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
