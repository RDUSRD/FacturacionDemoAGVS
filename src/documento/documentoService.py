from sqlalchemy.orm import Session
from src.documento.docModel import Documento
from decimal import Decimal

# importando los esquemas necesarios
from src.documento.factura.facturaSchema import FacturaSchema
from src.documento.orden_entrega.ordenEntregaSchema import OrdenEntregaSchema
from src.documento.notas.notaSchema import NotaCreditoSchema, NotaDebitoSchema

# Importando servicios de empresa y cliente
from src.empresa.empresaService import get_empresa_by_id
from src.cliente.clienteService import get_cliente_by_id
from src.documento.factura.facModel import Factura
from src.documento.orden_entrega.ordenEntregaModel import OrdenEntrega
from src.documento.notas.notaModel import NotaCredito, NotaDebito
from src.documento.factura.iva.ivaModel import iva
from src.documento.factura.operacion.operacionModel import Operacion
from src.documento.factura.detalleFactura.detalleFacturaModel import DetalleFactura
from src.pedidos.pedidoModel import Pedido  # Importar el modelo Pedido
from src.pedidos.pedidoService import convert_pedido
from src.monedas.dolar.dolarService import obtener_dolar_bcv
from datetime import datetime
import random


# Funciones para obtener documentos
def get_all_documentos(db: Session):
    return db.query(Documento).all()


def get_documento_by_id(db: Session, documento_id: int):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if documento:
        detalles_factura = (
            db.query(DetalleFactura)
            .filter(DetalleFactura.factura_id == documento.factura_id)
            .all()
        )
        impuestos = db.query(iva).filter(iva.factura_id == documento.factura_id).all()
        operaciones = (
            db.query(Operacion)
            .filter(Operacion.factura_id == documento.factura_id)
            .all()
        )
        return {
            "documento": documento,
            "detalles_factura": detalles_factura,
            "impuestos": impuestos,
            "operaciones": operaciones,
        }
    return None


def get_documento_by_numero_control(db: Session, numero_control: str):
    return (
        db.query(Documento).filter(Documento.numero_control == numero_control).first()
    )


def get_documentos_by_empresa_id(db: Session, empresa_id: int):
    return db.query(Documento).filter(Documento.empresa_id == empresa_id).all()


def get_documentos_by_cliente_id(db: Session, cliente_id: int):
    return db.query(Documento).filter(Documento.cliente_id == cliente_id).all()


# Funcion para asignar un número de control único a una factura
def generate_unique_numero_control(db: Session) -> str:
    """Genera un número de control único como cadena para una factura."""
    while True:
        numero_control = str(random.randint(10000000, 99999999))
        if (
            not db.query(Factura)
            .filter(Factura.numero_control == numero_control)
            .first()
        ):
            return numero_control
        # Si el número de control ya existe, se genera uno nuevo
        print(f"Número de control {numero_control} ya existe. Generando uno nuevo...")


# Funciones para crear documentos
# Estas funciones manejan la creación de documentos y sus relaciones con otros modelos
def get_or_create_factura(db: Session, documento_data: FacturaSchema):
    try:
        print("Iniciando creación de factura desde pedido...")

        # Buscar el pedido
        pedido = db.query(Pedido).filter(Pedido.id == documento_data.pedido_id).first()
        if not pedido:
            print("Error: El pedido no existe.")
            db.rollback()
            return {"error": "El pedido no existe."}

        # Validar el estado del pedido
        if pedido.estado != "pendiente":
            print("Error: El pedido no está en un estado válido para facturación.")
            db.rollback()
            return {"error": "El pedido ya fue convertido a factura.", "pedido_id": pedido.id, "estado": pedido.estado}

        # obtener el precio del BCV
        precio_bcv = obtener_dolar_bcv(db)
        if not isinstance(precio_bcv, (int, float)) or precio_bcv <= 0:
            print("Error: El precio del BCV no es válido.")
            db.rollback()
            return {"error": "El precio del BCV no es válido."}

        # Crear la factura
        factura = Factura(
            tipo_documento="Factura",
            estado="En espera",
            empresa_id=pedido.empresa_id,
            cliente_id=pedido.cliente_id,
            pedido_id=pedido.id,  # Asignar el pedido relacionado
            fecha_emision=datetime.today().date(),
            hora_emision=datetime.now().time(),
            aplica_igtf=documento_data.aplica_igtf,
        )
        db.add(factura)
        db.commit()
        db.refresh(factura)
        print(f"Factura creada: {factura}")

        # Inicializar variables para cálculos
        monto_exento = 0
        monto_base = 0
        descuento_total = 0

        # Procesar los detalles del pedido y convertirlos en detalles de factura
        for detalle_pedido in pedido.detalles:
            print(f"Procesando detalle del pedido: {detalle_pedido}")

            total_producto = detalle_pedido.cantidad * detalle_pedido.precio_unitario
            descuento_producto = detalle_pedido.descuento * detalle_pedido.cantidad
            descuento_total += descuento_producto
            print(
                f"Total del producto: {total_producto}, Descuento aplicado: {descuento_producto}"
            )

            if detalle_pedido.producto.exento:
                print("Producto exento, no se aplica IVA.")
                monto_exento += total_producto
            else:
                monto_base += total_producto

            # Crear detalle de factura
            detalle_factura = DetalleFactura(
                factura_id=factura.factura_id,
                producto_id=detalle_pedido.producto_id,
                cantidad=detalle_pedido.cantidad,
                total=total_producto,
            )
            db.add(detalle_factura)
            print(f"Detalle de factura creado: {detalle_factura}")

        print(
            f"Monto exento: {monto_exento}, Monto base: {monto_base}, Descuento total: {descuento_total}"
        )

        # Calcular impuestos
        iva_monto = round(monto_base * Decimal("0.16"), 2)
        print(f"IVA calculado: {iva_monto}")

        # Verificar si aplica el IGTF
        monto_igtf = 0
        if factura.aplica_igtf:
            monto_igtf = round(monto_base * Decimal("0.03"), 2)
            print(f"IGTF calculado: {monto_igtf}")
            monto_dolares = round(monto_base / Decimal(precio_bcv), 2) if precio_bcv else 0

        # Calcular el total de la factura
        subtotal = monto_base - descuento_total + iva_monto
        total_factura = subtotal + monto_igtf
        print(f"Subtotal: {subtotal}, Total factura: {total_factura}")

        # Actualizar la factura con los cálculos
        factura.total = total_factura
        factura.descuento_total = descuento_total
        factura.monto_igtf = monto_igtf
        factura.monto_dolares = monto_dolares if factura.aplica_igtf else 0.0
        db.add(factura)
        db.commit()
        db.refresh(factura)

        # Crear impuestos
        impuesto = iva(
            factura_id=factura.factura_id,
            base=monto_base,
            monto=iva_monto,
            monto_exento=monto_exento,
        )
        db.add(impuesto)

        # Crear operación
        operacion = create_operacion(
            db, factura_id=factura.factura_id, tipo="Venta", monto=monto_base
        )
        db.add(operacion)
        db.commit()
        db.refresh(operacion)
        print(f"Operación creada: {operacion}")

        # Actualizar el estado del pedido
        pedido.estado = "facturado"
        db.commit()
        print("Pedido actualizado a estado 'facturado'.")

        print("Factura creada exitosamente.")

        # Convertir el pedido a factura
        convert_pedido(db, pedido.id)  # Convertir el pedido a factura
        return {"factura creada": factura, "pedido_id": pedido.id}

    except Exception as e:
        print(f"Error al crear la factura: {str(e)}")

        # Rollback manual: eliminar entidades creadas
        if "factura" in locals():
            db.query(DetalleFactura).filter(
                DetalleFactura.factura_id == factura.factura_id
            ).delete()
            db.query(iva).filter(iva.factura_id == factura.factura_id).delete()
            db.query(Operacion).filter(
                Operacion.factura_id == factura.factura_id
            ).delete()
            db.query(Factura).filter(Factura.factura_id == factura.factura_id).delete()
            db.commit()
            print("Rollback manual ejecutado: entidades eliminadas.")

        db.rollback()
        return {"error": f"Ocurrió un error al crear la factura: {str(e)}"}


def get_or_create_nota_credito(db: Session, documento_data: NotaCreditoSchema):
    try:
        factura = (
            db.query(Factura).filter(Factura.id == documento_data.factura_id).first()
        )
        if not factura:
            return {"error": "La factura asociada no existe."}

        nota_credito = NotaCredito(
            tipo_documento="NotaCredito",
            numero_control=documento_data.numero_control,
            factura_id=factura.id,
            monto_credito=documento_data.monto_credito,
            descripcion=documento_data.descripcion,
            fecha_emision=datetime.today().date(),
            hora_emision=datetime.now().time(),
        )

        db.add(nota_credito)
        db.commit()
        db.refresh(nota_credito)

        return nota_credito
    except Exception as e:
        db.rollback()
        return {"error": f"Ocurrió un error al crear la nota de crédito: {str(e)}"}


def get_or_create_nota_debito(db: Session, documento_data: NotaDebitoSchema):
    try:
        factura = (
            db.query(Factura).filter(Factura.id == documento_data.factura_id).first()
        )
        if not factura:
            return {"error": "La factura asociada no existe."}

        nota_debito = NotaDebito(
            tipo_documento="NotaDebito",
            numero_control=documento_data.numero_control,
            factura_id=factura.id,
            monto_debito=documento_data.monto_debito,
            descripcion=documento_data.descripcion,
            fecha_emision=datetime.today().date(),
            hora_emision=datetime.now().time(),
        )

        db.add(nota_debito)
        db.commit()
        db.refresh(nota_debito)

        return nota_debito
    except Exception as e:
        db.rollback()
        return {"error": f"Ocurrió un error al crear la nota de débito: {str(e)}"}


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


def create_operacion(db: Session, factura_id: int, tipo: str, monto: float):
    """Crea una operación relacionada con una factura."""
    operacion = Operacion(factura_id=factura_id, tipo=tipo, monto=monto)
    db.add(operacion)
    db.commit()
    db.refresh(operacion)
    return operacion


def assign_numero_control(db: Session, factura_id: int):
    try:
        # Obtener la factura por ID
        factura = db.query(Factura).filter(Factura.factura_id == factura_id).first()
        if not factura:
            return {"error": "La factura no existe."}

        # Generar un número de control único
        numero_control = generate_unique_numero_control(db)
        factura.numero_control = numero_control
        factura.fecha_numero_control = datetime.today().date()
        factura.hora_numero_control = datetime.now().time()

        # Guardar los cambios en la base de datos
        db.add(factura)
        db.commit()
        db.refresh(factura)

        print(f"Número de control asignado: {numero_control}")
        return factura

    except Exception as e:
        db.rollback()
        print(f"Error al asignar el número de control: {str(e)}")
        return {"error": f"Ocurrió un error al asignar el número de control: {str(e)}"}
