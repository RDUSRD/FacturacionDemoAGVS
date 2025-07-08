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
from src.detalleFactura.detalleFacturaModel import DetalleFactura
from src.producto.prodModel import Producto
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
        print("Iniciando creación de factura...")

        # Verificar si la empresa y el cliente existen
        empresa = get_empresa_by_id(db, documento_data.empresa_id)
        print(f"Empresa obtenida: {empresa}")
        cliente = get_cliente_by_id(db, documento_data.cliente_id)
        print(f"Cliente obtenido: {cliente}")

        if not empresa:
            print("Error: La empresa no existe.")
            db.rollback()
            return {"error": "La empresa no existe."}
        if not cliente:
            print("Error: El cliente no existe.")
            db.rollback()
            return {"error": "El cliente no existe."}

        try:
            # Crear la factura inicialmente con datos básicos
            factura = Factura(
                tipo_documento=documento_data.tipo_documento,
                estado="En espera",  # Asignamos un estado por defecto
                empresa_id=documento_data.empresa_id,
                cliente_id=documento_data.cliente_id,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time(),
                aplica_igtf=documento_data.aplica_igtf,
                
            )
            db.add(factura)
            db.commit()
            db.refresh(factura)
            print(f"Factura creada: {factura}")

            # Inicializamos variables para cálculos
            monto_exento = 0
            monto_base = 0
            descuento_total = 0  # Inicializamos el descuento total

            # Confirmar que la factura existe y está confirmada
            factura_confirmada = (
                db.query(Factura)
                .filter(Factura.factura_id == factura.factura_id)
                .first()
            )
            if not factura_confirmada:
                print(
                    "Error: La factura no se ha confirmado correctamente en la base de datos."
                )
                db.rollback()
                return {
                    "error": "La factura no se ha confirmado correctamente en la base de datos."
                }
            print(f"Factura confirmada: {factura_confirmada}")

            # Procesamos los detalles de factura
            for detalle_data in documento_data.detalles_factura:
                print(f"Procesando detalle: {detalle_data}")
                producto = (
                    db.query(Producto)
                    .filter(Producto.id == detalle_data["producto_id"])
                    .first()
                )
                print(f"Producto obtenido: {producto}")
                if not producto:
                    print("Error: El producto no existe.")
                    db.rollback()
                    return {
                        "error": "El producto no existe y es requerido para crear un detalle de factura."
                    }

                if detalle_data["cantidad"] <= 0:
                    print("Error: La cantidad debe ser mayor a 0.")
                    db.rollback()
                    return {"error": "La cantidad debe ser mayor a 0."}

                total_producto = detalle_data["cantidad"] * producto.precio
                print(f"Total del producto calculado: {total_producto}")

                # Calcular descuento del producto
                descuento_producto = (
                    detalle_data.get("descuento", 0) * detalle_data["cantidad"]
                )
                descuento_total += descuento_producto
                print(f"Descuento del producto calculado: {descuento_producto}")

                if producto.exento:
                    monto_exento += total_producto
                else:
                    monto_base += total_producto

                monto_base_con_exento = monto_base + monto_exento

                # Crear detalle de factura
                detalle_factura = DetalleFactura(
                    factura_id=factura.factura_id,
                    producto_id=detalle_data["producto_id"],
                    cantidad=detalle_data["cantidad"],
                    total=total_producto,
                )
                db.add(detalle_factura)
                print(f"Detalle de factura creado: {detalle_factura}")

            print(
                f"Monto exento: {monto_exento}, Monto base: {monto_base}, Descuento total: {descuento_total}"
            )

            # Calculamos impuestos
            iva_monto = round(
                monto_base * Decimal("0.16"), 2
            )  # Calculamos el IVA sobre el monto base sin descuento
            print(f"IVA calculado: {iva_monto}")
            monto_base_con_descuento = (
                monto_base - descuento_total
            )  # Aplicamos el descuento al monto base

            # Verificamos si aplica el IGTF
            monto_igtf = 0
            if factura.aplica_igtf:
                monto_igtf = round(
                    monto_base * Decimal("0.03"), 2
                )  # Calculamos el 3% del monto base
                print(f"IGTF calculado: {monto_igtf}")

            # Calculamos el subtotal y total de la factura
            subtotal = (
                monto_base_con_descuento + iva_monto
            )  # Sumamos el IVA al monto base con descuento
            total_factura = subtotal + monto_igtf  # Agregamos el IGTF al subtotal
            print(
                f"Monto base con descuento: {monto_base_con_descuento}, Subtotal calculado: {subtotal}, Total con IGTF: {total_factura}"
            )

            # Definimos los impuestos después de calcular el IVA
            impuestos = [
                {"base": monto_base, "monto": iva_monto, "monto_exento": monto_exento}
            ]
            print(f"Impuestos definidos: {impuestos}")

            # Actualizamos la factura con los cálculos
            factura.total = total_factura
            factura.descuento_total = (
                descuento_total  # Guardamos el descuento total en la factura
            )
            factura.monto_igtf = monto_igtf  # Guardamos el monto del IGTF en la factura
            db.add(factura)
            db.commit()
            db.refresh(factura)

            for impuesto_data in impuestos:
                impuesto = iva(factura_id=factura.factura_id, **impuesto_data)
                db.add(impuesto)

            # Guardar las operaciones relacionadas con la factura
            operacion = create_operacion(
                db,
                factura_id=factura.factura_id,
                tipo="Venta",
                monto=monto_base_con_exento,
            )
            db.add(operacion)
            db.commit()
            db.refresh(operacion)
            print(f"Operación guardada: {operacion}")

            db.commit()
            print("Factura creada exitosamente.")
            return factura

        except Exception as e:
            print(f"Error interno al procesar la factura: {str(e)}")
            db.rollback()
            return {
                "error": f"Ocurrió un error interno al procesar la factura: {str(e)}"
            }

    except Exception as e:
        print(f"Error general al crear la factura: {str(e)}")
        db.rollback()
        return {"error": f"Ocurrió un error general al crear la factura: {str(e)}"}


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
