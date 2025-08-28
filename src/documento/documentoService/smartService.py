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
        "subtotal": to_float("subtotal", impuestos.subtotal_productos),
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
                "descuento": to_float(
                    "descuento", detalle.descuento
                ),  # Valor en moneda
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


def generar_json_imprenta_notas(
    nota,
    detalles,
    cliente: ClienteSchema,
    empresa: EmpresaSchema,
    precio_bcv: float,
    tipo_documento: int,
    factura_nro_control: str,
):
    print(f"detalles: {detalles}")
    # Convertir a minúsculas para evitar problemas de escritura
    tipo_cedula_lower = cliente.tipo_documento.lower()

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

    # Generar el JSON específico para notas
    json_data = {
        "rif": empresa.rif,
        "trackingid": "",  # Vacío para notas
        "nombrecliente": cliente.nombre,
        "rifcedulacliente": cliente.documento,
        "emailcliente": cliente.email,
        "telefonocliente": cliente.telefono,
        "idtipocedulacliente": idtipocedulacliente,
        "idtipodocumento": tipo_documento,
        "direccioncliente": cliente.domicilio_fiscal,
        "subtotal": to_float("subtotal", nota.modif_documento["subtotal_productos"]),
        "exento": to_float("exento", nota.modif_documento["monto_exento"]),
        "tasag": to_float("tasag", nota.modif_documento["iva_general"]),
        "baseg": to_float("baseg", nota.modif_documento["monto_base_general"]),
        "impuestog": to_float("impuestog", nota.modif_documento["iva_general_monto"]),
        "tasar": to_float("tasar", nota.modif_documento["iva_reducida"]),
        "baser": to_float("baser", nota.modif_documento["monto_base_reducida"]),
        "impuestor": to_float("impuestor", nota.modif_documento["iva_reducida_monto"]),
        "tasaa": to_float("tasaa", nota.modif_documento["iva_adicional"]),
        "basea": to_float("basea", nota.modif_documento["monto_base_adicional"]),
        "impuestoa": to_float("impuestoa", nota.modif_documento["iva_adicional_monto"]),
        "tasaigtf": to_float("tasaigtf", nota.modif_documento["igtf"]),
        "baseigtf": to_float("baseigtf", nota.modif_documento["base_igtf"]),
        "impuestoigtf": to_float("impuestoigtf", nota.modif_documento["monto_igtf"]),
        "total": to_float("total", nota.modif_documento["monto_total"]),
        "sendmail": "1" if SEND_EMAIL_SMART else "0",
        "relacionado": factura_nro_control,  # ID de la factura relacionada
        "sucursal": "",
        "numerointerno": (
            nota.nota_credito_id if tipo_documento == 3 else nota.nota_debito_id
        ),
        "tasacambio": to_float("tasacambio", precio_bcv),
        "Observacion": "Nota generada automáticamente.",
        "cuerpofactura": [
            {
                "codigo": detalle.get("producto_id"),
                "descripcion": detalle.get("descripcion", ""),
                "comentario": "",
                "precio": to_float("precio", detalle.get("precio_unitario", 0)),
                "cantidad": to_float("cantidad", detalle.get("cantidad", 0)),
                "tasa": to_float("tasa", detalle.get("alicuota_iva", 0)),
                "impuesto": (
                    to_float(
                        "impuesto",
                        detalle.get("total", 0) * detalle.get("alicuota_iva", 0) / 100,
                    )
                    if not detalle.get("exento", False)
                    else 0
                ),
                "descuento": to_float("descuento", detalle.get("descuento", 0)),
                "exento": detalle.get("exento", False),
                "monto": to_float("monto", detalle.get("total", 0)),
            }
            for detalle in detalles
        ],
        "formasdepago": "",
    }
    return json_data
