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
    subtotal_total_sin_descuento = 0
    subtotal_total_descuento = 0
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

        total_producto = detalle.cantidad * detalle.precio_unitario

        # Calcular el subtotal del producto
        subtotal_producto = total_producto - (total_producto * (detalle.descuento or 0))
        subtotal_total_descuento += subtotal_producto

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
        elif detalle.alicuota_iva == 15:
            monto_base_adicional += total_producto  # Base sin descuento
            iva_adicional_monto += round(total_producto * Decimal("0.15"), 4)

        # Aplicar descuento al total del producto
        descuento_producto = total_producto * (detalle.descuento or 0)
        descuento_total += descuento_producto

    # Calcular el monto total sumando las bases, IVA y restando descuentos
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
        "subtotal_descuento": round(float(max(subtotal_total_descuento, 0)), 4),
        "subtotal_sin_descuento": round(float(max(subtotal_total_sin_descuento, 0)), 4),
        "monto_base": round(float(max(
            monto_base_general + monto_base_reducida + monto_base_adicional, 0)
        ), 4),
        "monto_exento": round(float(max(monto_exento, 0)), 4),
        "monto_base_general": round(float(max(monto_base_general, 0)), 4),
        "monto_base_reducida": round(float(max(monto_base_reducida, 0)), 4),
        "monto_base_adicional": round(float(max(monto_base_adicional, 0)), 4),
        "descuento_total": round(float(max(descuento_total, 0)), 4),
        "iva_general": 16,  # Porcentaje de IVA general
        "iva_reducida": 8,  # Porcentaje de IVA reducida
        "iva_adicional": 15,  # Porcentaje de IVA adicional
        "iva_general_monto": round(float(max(iva_general_monto, 0)), 4),
        "iva_reducida_monto": round(float(max(iva_reducida_monto, 0)), 4),
        "iva_adicional_monto": round(float(max(iva_adicional_monto, 0)), 4),
        "igtf": 3,
        "base_igtf": round(float(max(monto_total, 0)), 4),  # Base para calculo del igtf
        "monto_igtf": round(float(max(monto_igtf, 0)), 4),
        "monto_dolares": round(float(max(monto_total / precio_bcv, 0)), 4) if precio_bcv else 0,
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
        "monto_dolares": round(float(totales.get("monto_total", 0) / totales.get("precio_bcv", 1)), 4),
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
