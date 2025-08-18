# region Imports
from datetime import datetime
import os
from decimal import Decimal

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
from src.producto.prodModel import Producto

from src.documento.documentoService.smartService import (
    generar_json_imprenta,
    enviar_a_imprenta,
)
from src.documento.documentoService.helperService import (
    rollback_manual,
    validar_existencia,
    calcular_totales,
    parse_factura,
    parse_nota_credito,
    parse_nota_debito,
    obtener_siguiente_id_documento,
    obtener_siguiente_id_factura,
    obtener_siguiente_id_nota_credito,
    obtener_siguiente_id_nota_debito,
)


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
            print(f"Totales calculados: {totales}")

            # Crear detalles de factura
            for detalle_pedido in pedido.detalles:
                detalle_factura = DetalleFactura(
                    factura_id=factura.factura_id,
                    producto_id=detalle_pedido.producto_id,
                    cantidad=detalle_pedido.cantidad,
                    alicuota_iva=detalle_pedido.alicuota_iva,
                    precio_unitario=detalle_pedido.precio_unitario,
                    total=detalle_pedido.cantidad * detalle_pedido.precio_unitario,
                )
                db.add(detalle_factura)

            # Calcular el valor de 'base' como la suma de las bases gravadas
            base_total = (
                totales["monto_base_general"]
                + totales["monto_base_reducida"]
                + totales["monto_base_adicional"]
            )

            # Crear impuestos con el valor calculado de 'base'
            impuesto = iva(
                factura_id=factura.factura_id,
                base=base_total,  # Asignar el valor calculado de 'base'
                monto_exento=totales["monto_exento"],
                monto_base_general=totales["monto_base_general"],
                monto_base_reducida=totales["monto_base_reducida"],
                monto_base_adicional=totales["monto_base_adicional"],
                iva_general=totales["iva_general"],
                iva_reducida=totales["iva_reducida"],
                iva_adicional=totales["iva_adicional"],
                monto=totales["monto_total"],
            )
            db.add(impuesto)

            if POST_SMART == "true":
                # Enviar a imprenta digital
                cliente = get_cliente_by_id(db, factura.cliente_id)
                empresa = get_empresa_by_id(db, factura.empresa_id)
                json_imprenta = generar_json_imprenta(
                    factura, pedido.detalles, cliente, empresa, impuesto, precio_bcv, 1
                )
                url_facturacion = f"{SMART_URL}/facturacion"  # URL de ejemplo, ajusta según sea necesario
                respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_facturacion)
                print(f"Respuesta de la API de imprenta: {respuesta_imprenta}")
                if "error" in respuesta_imprenta:
                    print(f"Error al enviar a imprenta: {respuesta_imprenta['error']}")

            # Actualizamos factura con mas datos
            factura.total = totales.get("monto_total", 0)
            factura.descuento_total = totales.get("descuento_total", 0)
            factura.monto_igtf = totales.get("monto_igtf", 0)
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
        print(f"Error inesperado: {str(e)}")
        rollback_manual(db, factura_id)  # Eliminar registros inconsistentes
        return {"error": f"Error inesperado: {str(e)}"}


# endregion


# region Notas de crédito
# Actualizar la lógica para obtener los detalles de la factura desde la tabla DetalleFactura
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

            # Obtener el precio del BCV
            precio_bcv = obtener_dolar_bcv(db)
            # Ajustar la validación para aceptar valores de tipo Decimal
            if not isinstance(precio_bcv, (int, float, Decimal)) or precio_bcv <= 0:
                raise ValueError("El precio del BCV no es válido.")

            # Inicializar variables para ajustes globales
            subtotal_ajustado = 0.0
            iva_ajustado = 0.0
            monto_exento_ajustado = 0.0
            monto_igtf_ajustado = 0.0
            total_ajustado = 0.0

            # Validar y procesar las modificaciones
            modificaciones_detalles = []
            for mod_detalle in documento_data.modif_detalles:
                # Verificar que el producto existe in los detalles de la factura
                detalle_existente = next(
                    (
                        d
                        for d in detalles_factura
                        if d.producto_id == mod_detalle["id_producto"]
                    ),
                    None,
                )

                if not detalle_existente:
                    raise ValueError(
                        f"Producto con ID {mod_detalle['id_producto']} no existe en los detalles de la factura."
                    )

                cantidad_ajustada = float(mod_detalle.get("cantidad", 0))
                precio_unitario_ajustado = float(mod_detalle.get("precio_unitario", 0))
                descuento_ajustado = float(mod_detalle.get("descuento", 0))

                # Validar que el descuento esté entre 0 y 1
                if not (0 <= descuento_ajustado <= 1):
                    raise ValueError(
                        f"Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                    )

                total_ajustado_detalle = (
                    cantidad_ajustada * precio_unitario_ajustado
                ) * (
                    1 - descuento_ajustado
                )  # Interpretar descuento como porcentaje

                modificaciones_detalles.append(
                    {
                        "id_producto": mod_detalle["id_producto"],
                        "cantidad": cantidad_ajustada,
                        "precio_unitario": precio_unitario_ajustado,
                        "descuento": descuento_ajustado,
                        "alicuota_iva": mod_detalle.get("alicuota_iva", 0),
                        "exento": mod_detalle.get("exento", False),
                        "total": total_ajustado_detalle,
                    }
                )

                # Actualizar los ajustes globales
                if mod_detalle.get("exento", False):
                    monto_exento_ajustado += total_ajustado_detalle
                else:
                    subtotal_ajustado += total_ajustado_detalle
                    iva_ajustado += total_ajustado_detalle * 0.16

            # Calcular el IGTF ajustado si aplica
            if factura.aplica_igtf:
                monto_base_total_ajustado = subtotal_ajustado + monto_exento_ajustado
                monto_igtf_ajustado = monto_base_total_ajustado * 0.03

            total_ajustado = (
                subtotal_ajustado
                + iva_ajustado
                + monto_exento_ajustado
                + monto_igtf_ajustado
            )

            # Crear la nota de crédito
            nota_credito = NotaCredito(
                id=documento_id,  # Asignar el ID calculado para documento
                nota_credito_id=nota_credito_id,  # Asignar el ID calculado para nota de crédito
                tipo_documento="NotaCredito",
                factura_id=factura.id,
                empresa_id=factura.empresa_id,
                cliente_id=factura.cliente_id,
                estado="creado",
                monto_credito=round(total_ajustado, 4),
                descripcion=documento_data.descripcion,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                modif_documento={
                    "monto_exento": round(monto_exento_ajustado, 4),
                    "monto_base_general": round(subtotal_ajustado, 4),
                    "monto_base_reducida": round(
                        0, 4
                    ),  # Ajustar si hay base reducida  # Ajustar si hay base adicional
                    "iva_general": round(iva_ajustado, 4),
                    "iva_reducida": round(0, 4),  # Ajustar si hay IVA reducido
                    "iva_adicional": round(0, 4),  # Ajustar si hay IVA adicional
                    "igtf": round(monto_igtf_ajustado, 4),
                },
                modif_detalles=modificaciones_detalles,
            )
            db.add(nota_credito)

            # Enviar a imprenta digital
            cliente = get_cliente_by_id(db, factura.cliente_id)
            empresa = get_empresa_by_id(db, factura.empresa_id)
            json_imprenta = generar_json_imprenta(
                nota_credito,
                nota_credito.modif_detalles,
                cliente,
                empresa,
                precio_bcv,
                3,
            )
            url_imprenta = "http://api.imprenta-digital.com/generar-nota-credito"  # URL de ejemplo, ajusta según sea necesario
            respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_imprenta)
            print(f"Respuesta de la API de imprenta: {respuesta_imprenta}")

            parsed_nota_credito = parse_nota_credito(nota_credito)
            return {"nota_credito": parsed_nota_credito, "factura_id": factura.id}

    except IntegrityError as e:
        print(f"Error de integridad: {str(e)}")
        rollback_manual(db, nota_credito_id)
        return {"error": f"Error de integridad: {str(e)}"}

    except ValueError as e:
        print(f"Error de validación: {str(e)}")
        rollback_manual(db, nota_credito_id)
        return {"error": f"Error de validación: {str(e)}"}

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        rollback_manual(db, nota_credito_id)
        return {"error": f"Error inesperado: {str(e)}"}


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
            nota_d_id = obtener_siguiente_id_nota_debito(db)

            # Validar que la factura asociada existe
            factura = (
                db.query(Factura)
                .filter(Factura.id == documento_data.factura_id)
                .first()
            )
            if not factura:
                raise ValueError("La factura asociada no existe.")

            # Obtener el precio del BCV
            precio_bcv = obtener_dolar_bcv(db)
            # Ajustar la validación para aceptar valores de tipo Decimal
            if not isinstance(precio_bcv, (int, float, Decimal)) or precio_bcv <= 0:
                raise ValueError("El precio del BCV no es válido.")

            # Inicializar variables para ajustes globales
            subtotal_ajustado = 0
            iva_ajustado = 0
            monto_exento_ajustado = 0
            monto_igtf_ajustado = 0
            total_ajustado = 0

            # Validar y procesar las modificaciones
            modificaciones_detalles = []
            for mod_detalle in documento_data.modif_detalles:
                # Verificar que el producto existe en la tabla Producto
                producto_existente = (
                    db.query(Producto)
                    .filter(Producto.id == mod_detalle["id_producto"])
                    .first()
                )
                if not producto_existente:
                    raise ValueError(
                        f"Producto con ID {mod_detalle['id_producto']} no existe en el inventario."
                    )

                cantidad_ajustada = mod_detalle.get("cantidad", 0)
                precio_unitario_ajustado = mod_detalle.get("precio_unitario", 0)
                descuento_ajustado = mod_detalle.get("descuento", 0)

                # Validar que el descuento esté entre 0 y 1
                if not (0 <= descuento_ajustado <= 1):
                    raise ValueError(
                        f"Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                    )

                total_ajustado_detalle = (
                    cantidad_ajustada * precio_unitario_ajustado
                ) * (
                    1 - descuento_ajustado
                )  # Interpretar descuento como porcentaje

                modificaciones_detalles.append(
                    {
                        "id_producto": mod_detalle["id_producto"],
                        "cantidad": cantidad_ajustada,
                        "precio_unitario": precio_unitario_ajustado,
                        "descuento": descuento_ajustado,
                        "alicuota_iva": mod_detalle.get("alicuota_iva", 0),
                        "exento": mod_detalle.get("exento", False),
                        "total": total_ajustado_detalle,
                    }
                )

                # Actualizar los ajustes globales
                if mod_detalle.get("exento", False):
                    monto_exento_ajustado += total_ajustado_detalle
                else:
                    subtotal_ajustado += total_ajustado_detalle
                    iva_ajustado += total_ajustado_detalle * 0.16

            # Calcular el IGTF ajustado si aplica
            if factura.aplica_igtf:
                monto_base_total_ajustado = subtotal_ajustado + monto_exento_ajustado
                monto_igtf_ajustado = monto_base_total_ajustado * 0.03

            total_ajustado = (
                subtotal_ajustado
                + iva_ajustado
                + monto_exento_ajustado
                + monto_igtf_ajustado
            )

            # Crear la nota de débito
            nota_debito = NotaDebito(
                id=documento_id,  # Asignar el ID calculado para documento
                nota_debito_id=nota_d_id,  # Asignar el ID calculado para nota de débito
                tipo_documento="NotaDebito",
                factura_id=factura.id,
                empresa_id=factura.empresa_id,
                cliente_id=factura.cliente_id,
                estado="creado",
                monto_debito=round(total_ajustado, 4),
                descripcion=documento_data.descripcion,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                modif_documento={
                    "monto_exento": round(monto_exento_ajustado, 4),
                    "monto_base_general": round(subtotal_ajustado, 4),
                    "monto_base_reducida": round(0, 4),  # Ajustar si hay base reducida
                    "monto_base_adicional": round(
                        0, 4
                    ),  # Ajustar si hay base adicional
                    "iva_general": round(iva_ajustado, 4),
                    "iva_reducida": round(0, 4),  # Ajustar si hay IVA reducido
                    "iva_adicional": round(0, 4),  # Ajustar si hay IVA adicional
                    "igtf": round(monto_igtf_ajustado, 4),
                },
                modif_detalles=modificaciones_detalles,
            )
            db.add(nota_debito)

            # Enviar a imprenta digital
            cliente = get_cliente_by_id(db, factura.cliente_id)
            empresa = get_empresa_by_id(db, factura.empresa_id)
            json_imprenta = generar_json_imprenta(
                nota_debito, modificaciones_detalles, cliente, empresa, precio_bcv, 2
            )
            url_imprenta = "http://api.imprenta-digital.com/generar-nota-debito"  # URL de ejemplo, ajusta según sea necesario
            respuesta_imprenta = enviar_a_imprenta(json_imprenta, url_imprenta)
            print(f"Respuesta de la API de imprenta: {respuesta_imprenta}")

            parsed_nota_debito = parse_nota_debito(nota_debito)
            return {"nota_debito": parsed_nota_debito, "factura_id": factura.id}

    except IntegrityError as e:
        print(f"Error de integridad: {str(e)}")
        rollback_manual(db, nota_d_id)
        return {"error": f"Error de integridad: {str(e)}"}

    except ValueError as e:
        print(f"Error de validación: {str(e)}")
        rollback_manual(db, nota_d_id)
        return {"error": f"Error de validación: {str(e)}"}

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        rollback_manual(db, nota_d_id)
        return {"error": f"Error inesperado: {str(e)}"}


# endregion
