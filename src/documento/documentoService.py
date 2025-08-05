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
from src.documento.factura.facturaService import create_operacion
from src.pedidos.pedidoModel import Pedido  # Importar el modelo Pedido
from src.pedidos.pedidoService import convert_pedido
from src.monedas.dolar.dolarService import obtener_dolar_bcv
from datetime import datetime
import random
from src.producto.prodModel import Producto  # Importar el modelo Producto


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


# Helpers
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


# Funciones para crear documentos
# Estas funciones manejan la creación de documentos y sus relaciones con otros modelos, sin asignacion de numero de control.
def get_or_create_factura(db: Session, documento_data: FacturaSchema):
    """
    Crea una factura a partir de un pedido existente.

    Este método valida que el pedido exista y esté en un estado válido para facturación.
    Luego, genera una factura asociada al pedido, calcula los impuestos, descuentos,
    y totales, y actualiza el estado del pedido a "facturado".

    Args:
        db (Session): Sesión de la base de datos.
        documento_data (FacturaSchema): Datos necesarios para crear la factura.

    Returns:
        dict: Contiene la factura creada y el ID del pedido asociado, o un mensaje de error.
    """
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
            return {
                "error": "El pedido ya fue convertido a factura.",
                "pedido_id": pedido.id,
                "estado": pedido.estado,
            }

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

            # Calcular el total del producto antes del descuento
            total_producto = detalle_pedido.cantidad * detalle_pedido.precio_unitario

            # Aplicar el descuento como porcentaje
            descuento_producto = total_producto * detalle_pedido.descuento  # descuento es un porcentaje (e.g., 0.1 para 10%)
            total_con_descuento = total_producto - descuento_producto

            descuento_total += descuento_producto
            print(
                f"Total del producto: {total_producto}, Descuento aplicado: {descuento_producto}, Total con descuento: {total_con_descuento}"
            )

            # Determinar si el producto es exento o no y actualizar los montos correspondientes
            if detalle_pedido.producto.exento:
                print("Producto exento, no se aplica IVA.")
                monto_exento += total_con_descuento
            else:
                monto_base += total_con_descuento

            # Crear detalle de factura
            detalle_factura = DetalleFactura(
                factura_id=factura.factura_id,
                producto_id=detalle_pedido.producto_id,
                cantidad=detalle_pedido.cantidad,
                total=total_con_descuento,  # Total después del descuento
            )
            db.add(detalle_factura)
            print(f"Detalle de factura creado: {detalle_factura}")

        print(
            f"Monto exento: {monto_exento}, Monto base: {monto_base}, Descuento total: {descuento_total}"
        )

        # Calcular impuestos
        iva_monto = round(monto_base * Decimal("0.16"), 2)
        print(f"IVA calculado: {iva_monto}")

        # Calcular el total de la factura
        subtotal = monto_base - descuento_total + iva_monto + monto_exento
        if subtotal < 0:
            print("Error: Subtotal negativo. Activando rollback manual.")
            raise Exception("Subtotal negativo. Activando rollback manual.")

        # Verificar si aplica el IGTF
        monto_igtf = 0
        if factura.aplica_igtf:
            monto_base_total = monto_base + monto_exento
            if monto_base_total > 0:
                monto_igtf = round(monto_base_total * Decimal("0.03"), 2)
                print(f"IGTF calculado: {monto_igtf}")
                monto_dolares = (
                    round(monto_base_total / Decimal(precio_bcv), 2)
                    if precio_bcv
                    else 0
                )
            else:
                print("Advertencia: IGTF no calculado porque el monto base total es 0.")

        total_factura = subtotal + monto_igtf
        if total_factura < 0:
            print("Error: Total de factura negativo. Activando rollback manual.")
            raise Exception("Total de factura negativo. Activando rollback manual.")

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
        factura = (
            db.query(Factura).filter(Factura.factura_id == factura.factura_id).first()
        )
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
        print("Iniciando creación de nota de crédito...")

        # Validar que la factura asociada existe
        factura = (
            db.query(Factura).filter(Factura.id == documento_data.factura_id).first()
        )
        if not factura:
            print("Error: La factura asociada no existe.")
            db.rollback()
            return {"error": "La factura asociada no existe."}

        # Validar que los detalles de la factura existen
        detalles_factura = (
            db.query(DetalleFactura)
            .filter(DetalleFactura.factura_id == factura.factura_id)
            .all()
        )
        if not detalles_factura:
            print("Error: No se encontraron detalles para la factura.")
            db.rollback()
            return {"error": "No se encontraron detalles para la factura."}

        # Inicializar variables para ajustes globales
        subtotal_ajustado = 0.0
        iva_ajustado = 0.0
        monto_exento_ajustado = 0.0
        monto_igtf_ajustado = 0.0
        total_ajustado = 0.0

        # Validar y procesar las modificaciones
        modificaciones_detalles = []
        for mod_detalle in documento_data.modif_detalles:
            # Verificar que el producto existe en los detalles de la factura anterior
            detalle_existente = next(
                (
                    d
                    for d in detalles_factura
                    if d.producto_id == mod_detalle["id_producto"]
                ),
                None,
            )

            if not detalle_existente:
                print(
                    f"Error: Producto con ID {mod_detalle['id_producto']} no existe en la factura anterior."
                )
                db.rollback()
                return {
                    "error": f"Producto con ID {mod_detalle['id_producto']} no existe en la factura anterior."
                }

            cantidad_ajustada = float(mod_detalle.get("cantidad", 0))
            precio_unitario_ajustado = float(mod_detalle.get("precio_unitario", 0))
            descuento_ajustado = float(mod_detalle.get("descuento", 0))

            # Validar que el descuento esté entre 0 y 1
            if not (0 <= descuento_ajustado <= 1):
                print(
                    f"Error: Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                )
                db.rollback()
                return {
                    "error": f"Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                }

            total_ajustado_detalle = (cantidad_ajustada * precio_unitario_ajustado) * (
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
            print(
                f"Subtotal ajustado: {subtotal_ajustado}, Monto exento ajustado: {monto_exento_ajustado}"
            )
            monto_base_total_ajustado = subtotal_ajustado + monto_exento_ajustado
            print(f"Monto base total ajustado: {monto_base_total_ajustado}")
            monto_igtf_ajustado = monto_base_total_ajustado * 0.03
            print(f"Monto IGTF ajustado: {monto_igtf_ajustado}")

        total_ajustado = (
            subtotal_ajustado
            + iva_ajustado
            + monto_exento_ajustado
            + monto_igtf_ajustado
        )
        print(f"Total ajustado: {total_ajustado}")

        # Crear la nota de crédito
        nota_credito = NotaCredito(
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
        db.commit()
        db.refresh(nota_credito)

        print(f"Nota de crédito creada: {nota_credito}")

        return {"nota_credito": nota_credito, "factura_id": factura.id}

    except Exception as e:
        print(f"Error al crear la nota de crédito: {str(e)}")

        # Rollback manual: eliminar entidades creadas
        if "nota_credito" in locals():
            db.query(NotaCredito).filter(NotaCredito.id == nota_credito.id).delete()
            db.commit()
            print("Rollback manual ejecutado: nota de crédito eliminada.")

        db.rollback()
        return {"error": f"Ocurrió un error al crear la nota de crédito: {str(e)}"}


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
        print("Iniciando creación de nota de débito...")

        # Validar que la factura asociada existe
        factura = (
            db.query(Factura).filter(Factura.id == documento_data.factura_id).first()
        )
        if not factura:
            print("Error: La factura asociada no existe.")
            db.rollback()
            return {"error": "La factura asociada no existe."}

        # Validar que los detalles de la factura existen
        detalles_factura = (
            db.query(DetalleFactura)
            .filter(DetalleFactura.factura_id == factura.factura_id)
            .all()
        )

        # Inicializar variables para ajustes globales
        subtotal_ajustado = 0
        iva_ajustado = 0
        monto_exento_ajustado = 0
        monto_igtf_ajustado = 0
        total_ajustado = 0

        # Validar y procesar las modificaciones
        modificaciones_detalles = []
        for mod_detalle in documento_data.modif_detalles:
            print(f"Procesando modificación de detalle: {mod_detalle}")
            # Verificar que el producto existe en la tabla Producto
            producto_existente = (
                db.query(Producto)
                .filter(Producto.id == mod_detalle["id_producto"])
                .first()
            )
            if not producto_existente:
                print(
                    f"Error: Producto con ID {mod_detalle['id_producto']} no existe en el inventario."
                )
                db.rollback()
                return {
                    "error": f"Producto con ID {mod_detalle['id_producto']} no existe en el inventario."
                }

            cantidad_ajustada = mod_detalle.get("cantidad", 0)
            precio_unitario_ajustado = mod_detalle.get("precio_unitario", 0)
            descuento_ajustado = mod_detalle.get("descuento", 0)

            # Validar que el descuento esté entre 0 y 1
            if not (0 <= descuento_ajustado <= 1):
                print(
                    f"Error: Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                )
                db.rollback()
                return {
                    "error": f"Descuento inválido para el producto ID {mod_detalle['id_producto']}. Debe estar entre 0 y 1."
                }

            total_ajustado_detalle = (cantidad_ajustada * precio_unitario_ajustado) * (
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
            print(
                f"Subtotal ajustado: {subtotal_ajustado}, Monto exento ajustado: {monto_exento_ajustado}"
            )
            monto_base_total_ajustado = subtotal_ajustado + monto_exento_ajustado
            print(f"Monto base total ajustado: {monto_base_total_ajustado}")
            monto_igtf_ajustado = monto_base_total_ajustado * 0.03
            print(f"Monto IGTF ajustado: {monto_igtf_ajustado}")

        total_ajustado = (
            subtotal_ajustado
            + iva_ajustado
            + monto_exento_ajustado
            + monto_igtf_ajustado
        )
        print(f"Total ajustado: {total_ajustado}")

        # Crear la nota de débito
        nota_debito = NotaDebito(
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
        db.commit()
        db.refresh(nota_debito)

        print(f"Nota de débito creada: {nota_debito}")

        return {"nota_debito": nota_debito, "factura_id": factura.id}

    except Exception as e:
        print(f"Error al crear la nota de débito: {str(e)}")

        # Rollback manual: eliminar entidades creadas
        if "nota_debito" in locals():
            db.query(NotaDebito).filter(NotaDebito.id == nota_debito.id).delete()
            db.commit()
            print("Rollback manual ejecutado: nota de débito eliminada.")

        db.rollback()
        return {"error": f"Ocurrió un error al crear la nota de débito: {str(e)}"}


# funciones sin usar aun.
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
