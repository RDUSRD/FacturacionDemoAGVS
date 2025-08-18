# region Helpers
# Función para manejar rollback manual
from decimal import Decimal
from pydoc import text
from requests import Session
from documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura
from documento.factura.facModel import Factura
from documento.factura.iva.ivaModel import iva
from documento.notas.notaModel import NotaCredito, NotaDebito


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
    monto_base_general = 0
    monto_base_reducida = 0
    monto_base_adicional = 0
    descuento_total = 0

    for detalle in detalles:
        if not (0 <= (detalle.descuento or 0) <= 1):
            raise ValueError(
                f"El descuento del producto con ID {detalle.producto_id} es inválido: {detalle.descuento}"
            )

        total_producto = detalle.cantidad * detalle.precio_unitario

        # Calcular IVA antes de aplicar el descuento
        if detalle.producto.exento:
            monto_exento += total_producto
        elif detalle.alicuota_iva == 16:
            monto_base_general += total_producto
        elif detalle.alicuota_iva == 8:
            monto_base_reducida += total_producto
        elif detalle.alicuota_iva == 15:
            monto_base_adicional += total_producto

        # Aplicar descuento después de calcular el IVA
        descuento_producto = total_producto * (detalle.descuento or 0)
        descuento_total += descuento_producto

    # Calcular IVA basado en las bases acumuladas
    iva_general_monto = round(monto_base_general * Decimal("0.16"), 4)
    iva_reducida_monto = round(monto_base_reducida * Decimal("0.08"), 4)
    iva_adicional_monto = round(monto_base_adicional * Decimal("0.15"), 4)

    # Calcular el monto total sumando las bases, IVA y restando descuentos
    monto_total = (
        monto_base_general
        + iva_general_monto
        + monto_base_reducida
        + iva_reducida_monto
        + monto_base_adicional
        + iva_adicional_monto
        + monto_exento
        - descuento_total
    )

    # Calcular IGTF si aplica
    monto_igtf = 0
    if aplica_igtf and monto_total > 0:
        monto_igtf = round(monto_total * Decimal("0.03"), 2)

    return {
        "monto_exento": max(monto_exento, 0),
        "monto_base_general": max(monto_base_general, 0),
        "monto_base_reducida": max(monto_base_reducida, 0),
        "monto_base_adicional": max(monto_base_adicional, 0),
        "descuento_total": max(descuento_total, 0),
        "iva_general": 16,  # Porcentaje de IVA general
        "iva_reducida": 8,  # Porcentaje de IVA reducida
        "iva_adicional": 15,  # Porcentaje de IVA adicional
        "iva_general_monto": max(iva_general_monto, 0),
        "iva_reducida_monto": max(iva_reducida_monto, 0),
        "iva_adicional_monto": max(iva_adicional_monto, 0),
        "monto_igtf": max(monto_igtf, 0),
        "monto_total": max(monto_total + monto_igtf, 0),
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
        db.query(NotaCredito.nota_credito_id)
        .order_by(NotaCredito.nota_credito_id.desc())
        .first()
    )
    return (ultimo_nota_credito_id[0] + 1) if ultimo_nota_credito_id else 1


# Función para obtener el siguiente ID disponible in la tabla nota_debito
def obtener_siguiente_id_nota_debito(db: Session):
    ultimo_nota_debito_id = (
        db.query(NotaDebito.nota_debito_id)
        .order_by(NotaDebito.nota_debito_id.desc())
        .first()
    )
    return (ultimo_nota_debito_id[0] + 1) if ultimo_nota_debito_id else 1


# endregion