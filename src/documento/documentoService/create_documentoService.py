# region Imports
from datetime import datetime
import os
from decimal import Decimal
import traceback

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.cliente.clienteService import get_cliente_by_id
from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura
from src.documento.factura.facModel import Factura
from src.documento.factura.facturaSchema import FacturaSchema
from src.documento.factura.iva.ivaModel import iva
from src.documento.notas.notaModel import NotaCredito, NotaDebito
from src.documento.notas.notaSchema import NotaCreditoSchema, NotaDebitoSchema

# from src.documento.orden_entrega.ordenEntregaModel import OrdenEntrega
# from src.documento.orden_entrega.ordenEntregaSchema import OrdenEntregaSchema
from src.empresa.empresaService import get_empresa_by_id
from src.monedas.dolar.dolarService import obtener_dolar_bcv
from src.pedidos.pedidoModel import Pedido

from src.documento.documentoService.smartService import (
    generar_json_imprenta,
    generar_json_imprenta_notas,  # Importar la nueva función para notas
    enviar_a_imprenta,
)
from src.documento.documentoService.helperService import (
    rollback_manual,
    rollback_manual_nota_credito,
    rollback_manual_nota_debito,
    validar_existencia,
    calcular_totales,
    parse_factura,
    parse_nota_credito,
    parse_nota_debito,
    obtener_siguiente_id_documento,
    obtener_siguiente_id_factura,
    obtener_siguiente_id_nota_credito,
    obtener_siguiente_id_nota_debito,
    calcular_totales_nota,
)


def decimal_to_float(data):
    if isinstance(data, list):
        return [decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    return data


# endregion

POST_SMART = os.getenv("POST_SMART")
SMART_URL = os.getenv("SMART_URL")


# region Creación de documentos - Factura
# Función para crear una factura
def get_or_create_factura(db: Session, documento_data: FacturaSchema):
    try:
        with db.begin():  # Transacción atómica
            # Obtener los IDs calculados
            documento_id = obtener_siguiente_id_documento(db)
            factura_id = obtener_siguiente_id_factura(db)

            # Validar existencia del pedido
            pedido = validar_existencia(db, Pedido, documento_data.pedido_id, "Pedido")

            if pedido.estado != "pendiente":
                raise ValueError(
                    "El pedido no está en un estado válido para facturación."
                )

            # Obtener el precio del BCV
            precio_bcv = pedido.tasa_cambio
            # Ajustar la validación para aceptar valores de tipo Decimal
            if not isinstance(precio_bcv, (int, float, Decimal)) or precio_bcv <= 0:
                raise ValueError("El precio del BCV no es válido.")

            # Crear la factura
            factura = Factura(
                id=documento_id,  # Asignar el ID calculado para documento
                factura_id=factura_id,  # Asignar el ID calculado para factura
                tipo_documento="Factura",
                estado="En espera",
                empresa_id=pedido.empresa_id,
                cliente_id=pedido.cliente_id,
                pedido_id=pedido.id,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                aplica_igtf=documento_data.aplica_igtf,
                tasa_cambio=pedido.tasa_cambio,
            )
            db.add(factura)
            db.flush()  # Sincronizar para obtener el ID de la factura sin confirmar la transacción
            db.refresh(factura)  # Refrescar para obtener el ID generado

            # Calcular totales e impuestos
            totales = calcular_totales(pedido.detalles, factura.aplica_igtf, precio_bcv)

            # Crear detalles de factura
            for detalle_pedido in pedido.detalles:
                detalle_factura = DetalleFactura(
                    factura_id=factura.factura_id,
                    producto_id=detalle_pedido.producto_id,
                    cantidad=detalle_pedido.cantidad,
                    alicuota_iva=detalle_pedido.alicuota_iva,
                    descuento=detalle_pedido.descuento,
                    precio_unitario=detalle_pedido.precio_unitario,
                    total=detalle_pedido.total,
                )
                db.add(detalle_factura)

            # Crear impuestos con el valor calculado de 'base'
            impuesto = iva(
                factura_id=factura.factura_id,
                subtotal_productos=totales["subtotal_productos"],
                base=totales["monto_base"],  # Asignar el valor calculado de 'base'
                monto_exento=totales["monto_exento"],
                monto_base_general=totales["monto_base_general"],
                monto_base_reducida=totales["monto_base_reducida"],
                monto_base_adicional=totales["monto_base_adicional"],
                iva_general=totales["iva_general"],
                iva_general_monto=totales["iva_general_monto"],
                iva_reducida=totales["iva_reducida"],
                iva_reducida_monto=totales["iva_reducida_monto"],
                iva_adicional=totales["iva_adicional"],
                iva_adicional_monto=totales["iva_adicional_monto"],
                base_igtf=totales["base_igtf"],
                igtf=totales["igtf"],
                monto_igtf=totales["monto_igtf"],
                monto=totales["monto_total"],
            )
            db.add(impuesto)

            if POST_SMART == "true":
                # Enviar a imprenta digital
                cliente = get_cliente_by_id(db, factura.cliente_id)
                empresa = get_empresa_by_id(db, factura.empresa_id)
                json_imprenta = generar_json_imprenta(
                    factura,
                    pedido.detalles,
                    cliente,
                    empresa,
                    impuesto,
                    precio_bcv,
                    pedido.id,
                )
                print(f"JSON para imprenta: {json_imprenta}")
                url_facturacion = f"{SMART_URL}/facturacion"
                respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_facturacion)

                if "success" in respuesta_imprenta and respuesta_imprenta["success"]:
                    # Actualizar los campos con los datos de la respuesta
                    factura.numero_control = respuesta_imprenta["data"][
                        "numerodocumento"
                    ]
                    factura.fecha_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["fecha"], "%Y%m%d"
                    ).date()
                    factura.hora_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["hora"], "%H:%M:%S"
                    ).time()
                    factura.url_pdf = respuesta_imprenta["data"]["urlpdf"]
                    factura.estado = "Procesado a imprenta"
                else:
                    error_message = respuesta_imprenta.get("error", {}).get(
                        "message", "Desconocido"
                    )
                    print(
                        f"Error al enviar a imprenta: {error_message}, {respuesta_imprenta.get('data', {})}"
                    )
                    rollback_manual(
                        db, factura.factura_id
                    )  # Realizar rollback en caso de error
                    raise ValueError(f"Error al enviar a imprenta: {error_message}")

            # Actualizamos factura con mas datos
            factura.total = totales.get("monto_total", 0)
            factura.descuento_total = totales.get("descuento_total", 0)
            factura.monto_dolares = totales.get("monto_dolares", 0)
            # No es necesario llamar a update, los cambios se reflejan automáticamente al confirmar la transacción

            # Actualizar el estado del pedido
            pedido.estado = "procesado"
            db.add(pedido)

            fact = parse_factura(factura, totales)
            return {"factura creada": fact, "pedido_id": pedido.id}

    except IntegrityError as e:
        print(f"Error de integridad: {str(e)}")
        rollback_manual(db, factura_id)  # Eliminar registros inconsistentes
        return {"error": f"Error de integridad: {str(e)}"}

    except ValueError as e:
        print(f"Error de validación: {str(e)}")
        rollback_manual(db, factura_id)  # Eliminar registros inconsistentes
        return {"error": f"Error de validación: {str(e)}"}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error inesperado: {str(e)}")
        print(f"Traceback del error: {error_trace}")
        rollback_manual(db, factura_id)  # Eliminar registros inconsistentes
        return {"error": f"Error inesperado: {str(e)}", "traceback": error_trace}


# endregion


# region Notas de crédito
# Función para crear una nota de crédito
def get_or_create_nota_credito(db: Session, documento_data: NotaCreditoSchema):
    """
    Crea una nota de crédito asociada a una factura existente.

    Este método valida que la factura exista y que los productos especificados en
    las modificaciones existan en los detalles de la factura. Calcula los ajustes
    globales (subtotal, IVA, monto exento, IGTF, total) basados en las modificaciones
    de los detalles y registra estos ajustes en la nota de crédito.

    Args:
        db (Session): Sesión de la base de datos.
        documento_data (NotaCreditoSchema): Datos necesarios para crear la nota de crédito.

    Returns:
        dict: Contiene la nota de crédito creada y el ID de la factura asociada, o un mensaje de error.
    """
    try:
        with db.begin():  # Transacción atómica
            # Obtener los IDs calculados
            documento_id = obtener_siguiente_id_documento(db)  # ID para el documento
            nota_credito_id = obtener_siguiente_id_nota_credito(
                db
            )  # ID para la nota de crédito

            # Validar que la factura asociada existe
            factura = (
                db.query(Factura)
                .filter(Factura.factura_id == documento_data.factura_id)
                .first()
            )
            if not factura:
                raise ValueError(
                    f"La factura con ID {documento_data.factura_id} no existe. No se puede crear la nota de crédito."
                )

            # Obtener los detalles de la factura desde la tabla DetalleFactura
            detalles_factura = (
                db.query(DetalleFactura)
                .filter(DetalleFactura.factura_id == factura.factura_id)
                .all()
            )

            # Calcular totales e impuestos
            totales, modificaciones_detalles = calcular_totales_nota(
                detalles_factura,
                documento_data.modif_detalles,
                db,
                aplica_igtf=factura.aplica_igtf,
            )

            # Ajustar la serialización de modif_documento y modif_detalles
            modif_documento = decimal_to_float(totales)
            modif_detalles = decimal_to_float(modificaciones_detalles)

            # Crear la nota de crédito
            nota_credito = NotaCredito(
                id=documento_id,  # Asignar el ID calculado para documento
                nota_credito_id=nota_credito_id,  # Asignar el ID calculado para nota de crédito
                tipo_documento="NotaCredito",
                factura_id=factura.factura_id,
                empresa_id=factura.empresa_id,
                cliente_id=factura.cliente_id,
                estado="creado",
                monto_credito=round(totales["monto_total"], 4),
                descripcion=documento_data.descripcion,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                modif_documento=modif_documento,  # Guardar directamente como diccionario
                modif_detalles=modif_detalles,  # Guardar directamente como lista
            )
            db.add(nota_credito)

            if POST_SMART == "true":
                print("POST_SMART is true")
                # Enviar a imprenta digital para notas
                cliente = get_cliente_by_id(db, factura.cliente_id)
                empresa = get_empresa_by_id(db, factura.empresa_id)
                json_imprenta = generar_json_imprenta_notas(
                    nota_credito,
                    nota_credito.modif_detalles,
                    cliente,
                    empresa,
                    precio_bcv=obtener_dolar_bcv(db),
                    tipo_documento=3,  # Tipo de documento para nota de crédito
                    factura_nro_control=factura.numero_control,  # ID de la factura relacionada
                )
                print(f"JSON para imprenta de nota de crédito: {json_imprenta}")
                url_imprenta = (
                    f"{SMART_URL}/facturacion"  # Usar variable de entorno para la URL
                )
                respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_imprenta)

                print(f"Respuesta de imprenta: {respuesta_imprenta}")
                if "success" in respuesta_imprenta and respuesta_imprenta["success"]:
                    # Actualizar los campos con los datos de la respuesta
                    nota_credito.numero_control = respuesta_imprenta["data"][
                        "numerodocumento"
                    ]
                    nota_credito.fecha_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["fecha"], "%Y%m%d"
                    ).date()
                    nota_credito.hora_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["hora"], "%H:%M:%S"
                    ).time()
                    nota_credito.url_pdf = respuesta_imprenta["data"]["urlpdf"]
                    nota_credito.estado = "Procesado a imprenta"
                else:
                    error_message = respuesta_imprenta.get("error", {}).get(
                        "message", "Desconocido"
                    )
                    print(
                        f"Error al enviar a imprenta: {error_message}, {respuesta_imprenta.get('data', {})}"
                    )
                    rollback_manual_nota_credito(
                        db, nota_credito.nota_credito_id
                    )  # Realizar rollback en caso de error
                    raise ValueError(f"Error al enviar a imprenta: {error_message}")

            parsed_nota_credito = parse_nota_credito(nota_credito)
            return {"nota_credito": parsed_nota_credito, "factura_id": factura.id}

    except IntegrityError as e:
        print(f"Error de integridad: {str(e)}")
        rollback_manual_nota_credito(db, nota_credito.nota_credito_id)
        return {"error": f"Error de integridad: {str(e)}"}

    except ValueError as e:
        print(f"Error de validación: {str(e)}")
        rollback_manual_nota_credito(db, nota_credito.nota_credito_id)
        return {"error": f"Error de validación: {str(e)}"}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error inesperado: {str(e)}")
        print(f"Traceback del error: {error_trace}")
        rollback_manual_nota_credito(db, nota_credito.nota_credito_id)

        return {"error": f"Error inesperado: {str(e)}", "traceback": error_trace}


# endregion


# region Notas de débito
# Función para crear una nota de débito
def get_or_create_nota_debito(db: Session, documento_data: NotaDebitoSchema):
    """
    Crea una nota de débito asociada a una factura existente.

    Este método valida que la factura exista y permite agregar productos nuevos
    o modificar productos existentes en los detalles de la factura. Calcula los
    ajustes globales (subtotal, IVA, monto exento, IGTF, total) basados en las
    modificaciones de los detalles y registra estos ajustes en la nota de débito.

    Args:
        db (Session): Sesión de la base de datos.
        documento_data (NotaDebitoSchema): Datos necesarios para crear la nota de débito.

    Returns:
        dict: Contiene la nota de débito creada y el ID de la factura asociada, o un mensaje de error.
    """
    try:
        with db.begin():  # Transacción atómica
            # Obtener los IDs calculados
            documento_id = obtener_siguiente_id_documento(db)  # Definir documento_id
            nota_debito_id = obtener_siguiente_id_nota_debito(db)

            # Validar que la factura asociada existe
            factura = (
                db.query(Factura)
                .filter(Factura.id == documento_data.factura_id)
                .first()
            )
            if not factura:
                raise ValueError("La factura asociada no existe.")

            # Obtener los detalles de la factura desde la tabla DetalleFactura
            detalles_factura = (
                db.query(DetalleFactura)
                .filter(DetalleFactura.factura_id == factura.factura_id)
                .all()
            )

            # Calcular totales e impuestos
            totales, modificaciones_detalles = calcular_totales_nota(
                detalles_factura, documento_data.modif_detalles, db, True
            )

            # Crear la nota de débito
            nota_debito = NotaDebito(
                id=documento_id,  # Asignar el ID calculado para documento
                nota_debito_id=nota_debito_id,  # Asignar el ID calculado para nota de débito
                tipo_documento="NotaDebito",
                factura_id=factura.id,
                empresa_id=factura.empresa_id,
                cliente_id=factura.cliente_id,
                estado="creado",
                monto_debito=round(totales["monto_total"], 4),
                descripcion=documento_data.descripcion,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                modif_documento={
                    "subtotal_descuento": totales["subtotal_descuento"],
                    "subtotal_sin_descuento": totales["subtotal_sin_descuento"],
                    "base": totales["monto_base"],
                    "monto_exento": totales["monto_exento"],
                    "monto_base_general": totales["monto_base_general"],
                    "monto_base_reducida": totales["monto_base_reducida"],
                    "monto_base_adicional": totales["monto_base_adicional"],
                    "iva_general": totales["iva_general"],
                    "iva_general_monto": totales["iva_general_monto"],
                    "iva_reducida": totales["iva_reducida"],
                    "iva_reducida_monto": totales["iva_reducida_monto"],
                    "iva_adicional": totales["iva_adicional"],
                    "iva_adicional_monto": totales["iva_adicional_monto"],
                    "base_igtf": totales["base_igtf"],
                    "igtf": totales["igtf"],
                    "monto_igtf": totales["monto_igtf"],
                    "monto": totales["monto_total"],
                },
                modif_detalles=modificaciones_detalles,
            )
            db.add(nota_debito)

            if POST_SMART == "true":
                # Enviar a imprenta digital para notas
                cliente = get_cliente_by_id(db, factura.cliente_id)
                empresa = get_empresa_by_id(db, factura.empresa_id)
                json_imprenta = generar_json_imprenta_notas(
                    nota_debito,
                    nota_debito.modif_detalles,
                    cliente,
                    empresa,
                    precio_bcv=obtener_dolar_bcv(db),
                    tipo_documento=2,  # Tipo de documento para nota de débito
                    factura_relacionada_id=factura.id,  # ID de la factura relacionada
                )
                url_imprenta = (
                    f"{SMART_URL}/facturacion"  # Usar variable de entorno para la URL
                )
                respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_imprenta)

                if "success" in respuesta_imprenta and respuesta_imprenta["success"]:
                    # Actualizar los campos con los datos de la respuesta
                    nota_debito.numero_control = respuesta_imprenta["data"][
                        "numerodocumento"
                    ]
                    nota_debito.fecha_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["fecha"], "%Y%m%d"
                    ).date()
                    nota_debito.hora_numero_control = datetime.strptime(
                        respuesta_imprenta["data"]["hora"], "%H:%M:%S"
                    ).time()
                    nota_debito.url_pdf = respuesta_imprenta["data"]["urlpdf"]
                    nota_debito.estado = "Procesado a imprenta"
                else:
                    error_message = respuesta_imprenta.get("error", {}).get(
                        "message", "Desconocido"
                    )
                    print(
                        f"Error al enviar a imprenta: {error_message}, {respuesta_imprenta.get('data', {})}"
                    )
                    rollback_manual_nota_debito(
                        db, nota_debito.nota_debito_id
                    )  # Realizar rollback en caso de error
                    raise ValueError(f"Error al enviar a imprenta: {error_message}")

            parsed_nota_debito = parse_nota_debito(nota_debito)
            return {"nota_debito": parsed_nota_debito, "factura_id": factura.id}

    except IntegrityError as e:
        print(f"Error de integridad: {str(e)}")
        rollback_manual_nota_debito(db, nota_debito.nota_debito_id)
        return {"error": f"Error de integridad: {str(e)}"}

    except ValueError as e:
        print(f"Error de validación: {str(e)}")
        rollback_manual_nota_debito(db, nota_debito.nota_debito_id)
        return {"error": f"Error de validación: {str(e)}"}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error inesperado: {str(e)}")
        print(f"Traceback del error: {error_trace}")
        rollback_manual_nota_debito(db, nota_debito.nota_debito_id)
        return {"error": f"Error inesperado: {str(e)}", "traceback": error_trace}


# endregion
