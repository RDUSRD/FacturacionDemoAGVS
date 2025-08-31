# Función para manejar rollback manual
from decimal import Decimal
from requests import Session
from sqlalchemy.sql import text

from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura
from src.documento.factura.facModel import Factura
from src.documento.factura.iva.ivaModel import iva
from src.documento.notas.notaModel import NotaCredito, NotaDebito


def rollback_manual(db: Session, factura_id: int):
    try:
        db.query(DetalleFactura).filter(
            DetalleFactura.factura_id == factura_id
        ).delete()
        db.query(iva).filter(iva.factura_id == factura_id).delete()
        db.query(Factura).filter(Factura.factura_id == factura_id).delete()
        db.commit()  # Confirmar antes de eliminar el documento
    except Exception as e:
        print(f"Error durante el rollback manual: {str(e)}")


def rollback_manual_nota_credito(db: Session, nota_credito_id: int):
    try:
        db.query(NotaCredito).filter(
            NotaCredito.nota_credito_id == nota_credito_id
        ).delete()
        db.commit()  # Confirmar antes de eliminar el documento
    except Exception as e:
        print(f"Error durante el rollback manual de nota de crédito: {str(e)}")


def rollback_manual_nota_debito(db: Session, nota_debito_id: int):
    try:
        db.query(NotaDebito).filter(
            NotaDebito.nota_debito_id == nota_debito_id
        ).delete()
        db.commit()  # Confirmar antes de eliminar el documento
    except Exception as e:
        print(f"Error durante el rollback manual de nota de débito: {str(e)}")


# Función para validar existencia de entidades
def validar_existencia(db: Session, modelo, id, nombre_entidad):
    entidad = db.query(modelo).filter(modelo.id == id).first()
    if not entidad:
        raise ValueError(f"{nombre_entidad} con ID {id} no existe.")
    return entidad


# Función para calcular totales e impuestos
def calcular_totales(detalles, aplica_igtf, precio_bcv):
    subtotal_total_sin_descuento = 0
    monto_exento = 0
    monto_base_general = 0
    monto_base_reducida = 0
    monto_base_adicional = 0
    descuento_total = 0
    iva_general_monto = 0
    iva_reducida_monto = 0
    iva_adicional_monto = 0

    # Revisar y ajustar la lógica de cálculo en calcular_totales
    # Ajustar la lógica para calcular el IVA correctamente
    for detalle in detalles:
        if not (0 <= (detalle.descuento or 0) <= 1):
            raise ValueError(
                f"El descuento del producto con ID {detalle.producto_id} es inválido: {detalle.descuento}"
            )

        total_producto = Decimal(detalle.cantidad) * Decimal(detalle.precio_unitario)
        # Calcular el subtotal del producto sin descuento
        subtotal_total_sin_descuento += total_producto

        # Calcular IVA sobre el total del producto sin descuento
        if detalle.producto.exento:
            monto_exento += total_producto
        elif detalle.alicuota_iva == 16:
            monto_base_general += total_producto  # Base sin descuento
            iva_general_monto += round(total_producto * Decimal("0.16"), 4)
        elif detalle.alicuota_iva == 8:
            monto_base_reducida += total_producto  # Base sin descuento
            iva_reducida_monto += round(total_producto * Decimal("0.08"), 4)
        elif detalle.alicuota_iva == 31:
            monto_base_adicional += total_producto  # Base sin descuento
            iva_adicional_monto += round(total_producto * Decimal("0.31"), 4)

        # Aplicar descuento al total del producto
        descuento_producto = total_producto * Decimal(detalle.descuento or 0)
        descuento_total += descuento_producto

    # Calcular el monto total sumando las bases, IVA, restando descuentos y considerando exentos
    monto_total = (
        monto_base_general
        + iva_general_monto
        + monto_base_reducida
        + iva_reducida_monto
        + monto_base_adicional
        + iva_adicional_monto
        + monto_exento
    )

    # Calcular IGTF si aplica
    monto_igtf = 0
    if aplica_igtf and monto_total > 0:
        monto_igtf = round(monto_total * Decimal("0.03"), 2)

    return {
        "subtotal_productos": round(float(max(subtotal_total_sin_descuento, 0)), 4),
        "monto_base": round(
            float(
                max(monto_base_general + monto_base_reducida + monto_base_adicional, 0)
            ),
            4,
        ),
        "monto_exento": round(float(max(monto_exento, 0)), 4),
        "monto_base_general": round(float(max(monto_base_general, 0)), 4),
        "monto_base_reducida": round(float(max(monto_base_reducida, 0)), 4),
        "monto_base_adicional": round(float(max(monto_base_adicional, 0)), 4),
        "descuento_total": round(float(max(descuento_total, 0)), 4),
        "iva_general": 16,  # Porcentaje de IVA general
        "iva_reducida": 8,  # Porcentaje de IVA reducida
        "iva_adicional": 31,  # Porcentaje de IVA adicional, Se cambio de 15% a 31%, ya que es la suma de iva general mas 15%.
        "iva_general_monto": round(float(max(iva_general_monto, 0)), 4),
        "iva_reducida_monto": round(float(max(iva_reducida_monto, 0)), 4),
        "iva_adicional_monto": round(float(max(iva_adicional_monto, 0)), 4),
        "igtf": 3,
        "base_igtf": round(float(max(monto_total, 0)), 4),  # Base para calculo del igtf
        "monto_igtf": round(float(max(monto_igtf, 0)), 4),
        "monto_dolares": (
            round(float(max((monto_total + monto_igtf) / precio_bcv, 0)), 4)
            if precio_bcv
            else 0
        ),
        "monto_total": round(float(max(monto_total + monto_igtf, 0)), 4),
    }


# Función para parsear factura
def parse_factura(factura: Factura, totales: dict) -> dict:
    return {
        "id": factura.factura_id,
        "factura_id": factura.factura_id,
        "numero_control": factura.numero_control,
        "tipo_documento": factura.tipo_documento,
        "estado": factura.estado,
        "empresa_id": factura.empresa_id,
        "cliente_id": factura.cliente_id,
        "pedido_id": factura.pedido_id,
        "fecha_emision": factura.fecha_emision,
        "hora_emision": factura.hora_emision,
        "aplica_igtf": factura.aplica_igtf,
        "monto_dolares": round(
            float(totales.get("monto_total", 0) / totales.get("precio_bcv", 1)), 4
        ),
        "descuento_total": round(float(totales.get("descuento_total", 0)), 4),
        "total": round(float(totales.get("monto_total", 0)), 4),
        "monto_igtf": round(float(totales.get("monto_igtf", 0)), 4),
        "iva_general_monto": round(float(totales.get("iva_general_monto", 0)), 4),
        "iva_reducida_monto": round(float(totales.get("iva_reducida_monto", 0)), 4),
        "iva_adicional_monto": round(float(totales.get("iva_adicional_monto", 0)), 4),
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
        "monto_credito": round(float(nota_credito.monto_credito), 4),
        "descripcion": nota_credito.descripcion,
        "modif_documento": nota_credito.modif_documento,
        "modif_detalles": nota_credito.modif_detalles,
        "numero_control": nota_credito.numero_control,
        "fecha_numero_control": nota_credito.fecha_numero_control,
        "hora_numero_control": nota_credito.hora_numero_control,
        "url_pdf": nota_credito.url_pdf,
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
        "monto_debito": round(float(nota_debito.monto_debito), 4),
        "descripcion": nota_debito.descripcion,
        "modif_documento": nota_debito.modif_documento,
        "modif_detalles": nota_debito.modif_detalles,
        "numero_control": nota_debito.numero_control,
        "fecha_numero_control": nota_debito.fecha_numero_control,
        "hora_numero_control": nota_debito.hora_numero_control,
        "url_pdf": nota_debito.url_pdf,
    }


# Agregar funciones auxiliares para obtener el siguiente ID disponible
# Función para obtener el siguiente ID disponible en la tabla documento
def obtener_siguiente_id_documento(db: Session):
    try:
        # Consultar el último ID utilizado en la tabla documento usando text
        ultimo_documento_id = db.execute(text("SELECT MAX(id) FROM documento")).scalar()
        siguiente_id = (ultimo_documento_id + 1) if ultimo_documento_id else 1
        return f"{siguiente_id:08d}"  # Formatear con 8 dígitos
    except Exception as e:
        print(f"Error al obtener el siguiente ID de documento: {str(e)}")
        raise


# Función para obtener el siguiente ID disponible en la tabla factura
def obtener_siguiente_id_factura(db: Session):
    ultimo_factura_id = (
        db.query(Factura.factura_id).order_by(Factura.factura_id.desc()).first()
    )
    siguiente_id = (ultimo_factura_id[0] + 1) if ultimo_factura_id else 1
    return f"{siguiente_id:08d}"  # Formatear con 8 dígitos


# Función para obtener el siguiente ID disponible in la tabla nota_credito
def obtener_siguiente_id_nota_credito(db: Session):
    ultimo_nota_credito_id = (
        db.query(NotaCredito.nota_credito_id)
        .order_by(NotaCredito.nota_credito_id.desc())
        .first()
    )
    siguiente_id = (ultimo_nota_credito_id[0] + 1) if ultimo_nota_credito_id else 1
    return f"{siguiente_id:08d}"  # Formatear con 8 dígitos


# Función para obtener el siguiente ID disponible in la tabla nota_debito
def obtener_siguiente_id_nota_debito(db: Session):
    ultimo_nota_debito_id = (
        db.query(NotaDebito.nota_debito_id)
        .order_by(NotaDebito.nota_debito_id.desc())
        .first()
    )
    siguiente_id = (ultimo_nota_debito_id[0] + 1) if ultimo_nota_debito_id else 1
    return f"{siguiente_id:08d}"  # Formatear con 8 dígitos


# Mover funciones relacionadas con notas de crédito y débito al helper
def calcular_totales_nota(
    detalles_factura, modif_detalles, db, es_nota_debito=False, aplica_igtf=False
):
    """
    Calcula los totales e impuestos para notas de crédito o débito basados en las modificaciones.
    Si es una nota de débito, no se valida que el producto exista en los detalles de la factura,
    pero sí se valida que el producto exista en la tabla Producto.
    """
    from src.producto.prodModel import Producto  # Importar el modelo Producto

    monto_exento = 0
    monto_base_general = 0
    monto_base_reducida = 0
    monto_base_adicional = 0
    descuento_total = 0
    iva_general_monto = 0
    iva_reducida_monto = 0
    iva_adicional_monto = 0
    subtotal_productos = 0
    monto_igtf = 0

    modificaciones_detalles = []

    # Subtotales separados para exentos y no exentos
    subtotal_no_exento = 0  # Subtotal de productos no exentos
    subtotal_exento = 0  # Subtotal de productos exentos

    for mod_detalle in modif_detalles:
        # Validar que el producto exista en la tabla Producto
        producto = validar_existencia(
            db, Producto, mod_detalle["id_producto"], "Producto"
        )

        if not es_nota_debito:
            # Validar que el producto exista en los detalles de la factura
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

        cantidad = Decimal(mod_detalle.get("cantidad", 0))
        precio_unitario = Decimal(mod_detalle.get("precio_unitario", 0))
        descuento = Decimal(mod_detalle.get("descuento", 0))

        total_producto = round(cantidad * precio_unitario, 4)  # Redondear a 4 decimales
        descuento_producto = round(
            total_producto * descuento, 4
        )  # Redondear a 4 decimales
        total_producto_con_descuento = round(
            total_producto - descuento_producto, 4
        )  # Redondear a 4 decimales
        subtotal_productos = round(
            subtotal_productos + total_producto, 4
        )  # Redondear acumulado
        descuento_total = round(
            descuento_total + descuento_producto, 4
        )  # Redondear acumulado

        if mod_detalle.get("exento", False):
            monto_exento = round(
                monto_exento + total_producto_con_descuento, 4
            )  # Redondear acumulado
            subtotal_exento = round(
                subtotal_exento + total_producto_con_descuento, 4
            )  # Redondear acumulado
        else:
            subtotal_no_exento = round(
                subtotal_no_exento + total_producto_con_descuento, 4
            )  # Redondear acumulado
            alicuota_iva = mod_detalle.get("alicuota_iva", 0)
            if alicuota_iva == 16:
                monto_base_general = round(
                    monto_base_general + total_producto, 4
                )  # Redondear acumulado
                iva_general_monto = round(
                    iva_general_monto + total_producto * Decimal("0.16"), 4
                )  # Redondear acumulado
            elif alicuota_iva == 8:
                monto_base_reducida = round(
                    monto_base_reducida + total_producto, 4
                )  # Redondear acumulado
                iva_reducida_monto = round(
                    iva_reducida_monto + total_producto * Decimal("0.08"), 4
                )  # Redondear acumulado
            elif alicuota_iva == 31:
                monto_base_adicional = round(
                    monto_base_adicional + total_producto, 4
                )  # Redondear acumulado
                iva_adicional_monto = round(
                    iva_adicional_monto + total_producto * Decimal("0.31"), 4
                )  # Redondear acumulado

        modificaciones_detalles.append(
            {
                "producto_id": mod_detalle["id_producto"],
                "descripcion": producto.descripcion,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "descuento": descuento_producto,
                "alicuota_iva": mod_detalle.get("alicuota_iva", 0),
                "exento": mod_detalle.get("exento", False),
                "subtotal": total_producto,
                "total": total_producto_con_descuento,
            }
        )

    monto_total = round(
        monto_base_general
        + iva_general_monto
        + monto_base_reducida
        + iva_reducida_monto
        + monto_base_adicional
        + iva_adicional_monto
        + monto_exento,
        4,
    )

    if aplica_igtf and monto_total > 0:
        monto_igtf = round(monto_total * Decimal("0.03"), 2)

    total_general = round(monto_total + monto_igtf, 4)

    # Ajustar el cálculo del subtotal acumulado para que coincida con el subtotal calculado
    subtotal_productos = round(
        subtotal_no_exento + subtotal_exento + descuento_total, 4
    )  # Recalcular el subtotal acumulado sin aplicar el descuento

    return {
        "subtotal_productos": round(float(max(subtotal_productos, 0)), 4),
        "monto_base": round(
            float(
                max(monto_base_general + monto_base_reducida + monto_base_adicional, 0)
            ),
            4,
        ),
        "monto_exento": round(float(max(monto_exento, 0)), 4),
        "monto_base_general": round(float(max(monto_base_general, 0)), 4),
        "monto_base_reducida": round(float(max(monto_base_reducida, 0)), 4),
        "monto_base_adicional": round(float(max(monto_base_adicional, 0)), 4),
        "iva_general": 16,
        "iva_reducida": 8,
        "iva_adicional": 31,
        "iva_general_monto": round(float(max(iva_general_monto, 0)), 4),
        "iva_reducida_monto": round(float(max(iva_reducida_monto, 0)), 4),
        "iva_adicional_monto": round(float(max(iva_adicional_monto, 0)), 4),
        "igtf": 3,
        "base_igtf": round(float(max(monto_total, 0)), 4),
        "monto_igtf": round(float(max(monto_igtf, 0)), 4),
        "monto_total": round(float(max(total_general, 0)), 4),
    }, modificaciones_detalles
