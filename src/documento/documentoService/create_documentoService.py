# region Imports
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text  # Importar text para consultas SQL explícitas

from src.cliente.clienteService import get_cliente_by_id
from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura
from src.documento.factura.facModel import Factura
from src.documento.factura.facturaSchema import FacturaSchema
from src.documento.factura.iva.ivaModel import iva
from src.documento.notas.notaModel import NotaCredito, NotaDebito
from src.documento.notas.notaSchema import NotaCreditoSchema, NotaDebitoSchema
from src.documento.orden_entrega.ordenEntregaModel import OrdenEntrega
from src.documento.orden_entrega.ordenEntregaSchema import OrdenEntregaSchema
from src.empresa.empresaService import get_empresa_by_id
from src.monedas.dolar.dolarService import obtener_dolar_bcv
from src.pedidos.pedidoModel import Pedido
from src.producto.prodModel import Producto

# endregion


# region Helpers
# Función para manejar rollback manual
def rollback_manual(db: Session, factura_id: int):
    try:
        db.query(DetalleFactura).filter(
            DetalleFactura.factura_id == factura_id
        ).delete()
        db.query(iva).filter(iva.factura_id == factura_id).delete()
        db.query(Factura).filter(Factura.factura_id == factura_id).delete()
        db.commit()
    except Exception as e:
        print(f"Error durante el rollback manual: {str(e)}")


# Función para validar existencia de entidades
def validar_existencia(db: Session, modelo, id, nombre_entidad):
    entidad = db.query(modelo).filter(modelo.id == id).first()
    if not entidad:
        raise ValueError(f"{nombre_entidad} con ID {id} no existe.")
    return entidad


# Función para calcular totales e impuestos
def calcular_totales(detalles, aplica_igtf, precio_bcv):
    monto_exento = 0
    monto_base = 0
    descuento_total = 0

    for detalle in detalles:
        if not (0 <= (detalle.descuento or 0) <= 1):
            raise ValueError(
                f"El descuento del producto con ID {detalle.producto_id} es inválido: {detalle.descuento}"
            )

        total_producto = detalle.cantidad * detalle.precio_unitario
        descuento_producto = total_producto * (detalle.descuento or 0)
        total_con_descuento = total_producto - descuento_producto

        descuento_total += descuento_producto

        if detalle.producto.exento:
            monto_exento += total_con_descuento
        else:
            monto_base += total_con_descuento

    iva_monto = round(monto_base * Decimal("0.16"), 2)
    monto_igtf = 0
    if aplica_igtf and (monto_base + monto_exento) > 0:
        monto_igtf = round((monto_base + monto_exento) * Decimal("0.03"), 2)

    return {
        "monto_exento": max(monto_exento, 0),
        "monto_base": max(monto_base, 0),
        "descuento_total": max(descuento_total, 0),
        "iva_monto": max(iva_monto, 0),
        "monto_igtf": max(monto_igtf, 0),
    }


# Función para parsear factura
def parse_factura(factura: Factura, totales: dict) -> dict:
    return {
        "id": factura.factura_id,
        "tipo_documento": factura.tipo_documento,
        "estado": factura.estado,
        "empresa_id": factura.empresa_id,
        "cliente_id": factura.cliente_id,
        "pedido_id": factura.pedido_id,
        "fecha_emision": factura.fecha_emision,
        "hora_emision": factura.hora_emision,
        "aplica_igtf": factura.aplica_igtf,
        "monto_dolares": totales.get("monto_base", 0) + totales.get("monto_exento", 0),
        "descuento_total": totales.get("descuento_total", 0),
        "total": totales.get("monto_base", 0)
        + totales.get("iva_monto", 0)
        + totales.get("monto_exento", 0)
        + totales.get("monto_igtf", 0),
        "monto_igtf": totales.get("monto_igtf", 0),
    }


# Función para parsear nota de crédito
def parse_nota_credito(nota_credito: NotaCredito) -> dict:
    return {
        "id": nota_credito.id,
        "nota_credito_id": nota_credito.nota_credito_id,
        "tipo_documento": nota_credito.tipo_documento,
        "estado": nota_credito.estado,
        "empresa_id": nota_credito.empresa_id,
        "cliente_id": nota_credito.cliente_id,
        "factura_id": nota_credito.factura_id,
        "fecha_emision": nota_credito.fecha_emision,
        "hora_emision": nota_credito.hora_emision,
        "monto_credito": nota_credito.monto_credito,
        "descripcion": nota_credito.descripcion,
        "modif_documento": nota_credito.modif_documento,
        "modif_detalles": nota_credito.modif_detalles,
    }


# Función para parsear nota de débito
def parse_nota_debito(nota_debito: NotaDebito) -> dict:
    return {
        "id": nota_debito.id,
        "nota_debito_id": nota_debito.nota_debito_id,
        "tipo_documento": nota_debito.tipo_documento,
        "estado": nota_debito.estado,
        "empresa_id": nota_debito.empresa_id,
        "cliente_id": nota_debito.cliente_id,
        "factura_id": nota_debito.factura_id,
        "fecha_emision": nota_debito.fecha_emision,
        "hora_emision": nota_debito.hora_emision,
        "monto_debito": nota_debito.monto_debito,
        "descripcion": nota_debito.descripcion,
        "modif_documento": nota_debito.modif_documento,
        "modif_detalles": nota_debito.modif_detalles,
    }


# Agregar funciones auxiliares para obtener el siguiente ID disponible
# Función para obtener el siguiente ID disponible en la tabla documento
def obtener_siguiente_id_documento(db: Session):
    try:
        # Consultar el último ID utilizado en la tabla documento usando text
        ultimo_documento_id = db.execute(text("SELECT MAX(id) FROM documento")).scalar()
        return (ultimo_documento_id + 1) if ultimo_documento_id else 1
    except Exception as e:
        print(f"Error al obtener el siguiente ID de documento: {str(e)}")
        raise


# Función para obtener el siguiente ID disponible en la tabla factura
def obtener_siguiente_id_factura(db: Session):
    ultimo_factura_id = (
        db.query(Factura.factura_id).order_by(Factura.factura_id.desc()).first()
    )
    return (ultimo_factura_id[0] + 1) if ultimo_factura_id else 1


# Función para obtener el siguiente ID disponible en la tabla nota_credito
def obtener_siguiente_id_nota_credito(db: Session):
    ultimo_nota_credito_id = (
        db.query(NotaCredito.nota_credito_id).order_by(NotaCredito.nota_credito_id.desc()).first()
    )
    return (ultimo_nota_credito_id[0] + 1) if ultimo_nota_credito_id else 1


# Función para obtener el siguiente ID disponible en la tabla nota_debito
def obtener_siguiente_id_nota_debito(db: Session):
    ultimo_nota_debito_id = (
        db.query(NotaDebito.nota_debito_id).order_by(NotaDebito.nota_debito_id.desc()).first()
    )
    return (ultimo_nota_debito_id[0] + 1) if ultimo_nota_debito_id else 1


# endregion


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
            precio_bcv = obtener_dolar_bcv(db)
            if not isinstance(precio_bcv, (int, float)) or precio_bcv <= 0:
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
                    total=detalle_pedido.cantidad * detalle_pedido.precio_unitario,
                )
                db.add(detalle_factura)

            # Crear impuestos
            impuesto = iva(
                factura_id=factura.factura_id,
                base=totales["monto_base"],
                monto=totales["iva_monto"],
                monto_exento=totales["monto_exento"],
            )
            db.add(impuesto)

            # Actualizar el estado del pedido
            pedido.estado = "facturado"
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
            nota_credito_id = obtener_siguiente_id_nota_credito(db)  # ID para la nota de crédito

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

            # Inicializar variables para ajustes globales
            subtotal_ajustado = 0.0
            iva_ajustado = 0.0
            monto_exento_ajustado = 0.0
            monto_igtf_ajustado = 0.0
            total_ajustado = 0.0

            # Validar y procesar las modificaciones
            modificaciones_detalles = []
            for mod_detalle in documento_data.modif_detalles:
                # Verificar que el producto existe en los detalles de la factura
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
                    "subtotal": round(subtotal_ajustado, 4),
                    "iva": round(iva_ajustado, 4),
                    "monto_exento": round(monto_exento_ajustado, 4),
                    "igtf": round(monto_igtf_ajustado, 4),
                    "total": round(total_ajustado, 4),
                },
                modif_detalles=modificaciones_detalles,
            )
            db.add(nota_credito)

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
                    "subtotal": round(subtotal_ajustado, 4),
                    "iva": round(iva_ajustado, 4),
                    "monto_exento": round(monto_exento_ajustado, 4),
                    "igtf": round(monto_igtf_ajustado, 4),
                    "total": round(total_ajustado, 4),
                },
                modif_detalles=modificaciones_detalles,
            )
            db.add(nota_debito)

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


# region Orden de entrega
# Función para crear una orden de entrega
def get_or_create_orden_entrega(db: Session, documento_data: OrdenEntregaSchema):
    try:
        orden_entrega = (
            db.query(OrdenEntrega)
            .filter(OrdenEntrega.numero_control == documento_data.numero_control)
            .first()
        )

        if not orden_entrega:
            empresa = get_empresa_by_id(db, documento_data.empresa_id)
            if not empresa:
                return {"error": "La empresa asociada no existe."}

            cliente = get_cliente_by_id(db, documento_data.cliente_id)
            if not cliente:
                return {"error": "El cliente asociado no existe."}

            orden_entrega = OrdenEntrega(
                tipo_documento="OrdenEntrega",
                numero_control=documento_data.numero_control,
                empresa_id=empresa.id,
                cliente_id=cliente.id,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
            )

            db.add(orden_entrega)
            db.commit()
            db.refresh(orden_entrega)

        return orden_entrega
    except Exception as e:
        db.rollback()
        return {"error": f"Ocurrió un error al crear la orden de entrega: {str(e)}"}


# endregion
