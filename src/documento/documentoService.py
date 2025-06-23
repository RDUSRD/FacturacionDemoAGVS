from sqlalchemy.orm import Session
from src.documento.docModel import Documento

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
from src.documento.factura.operacion.operacionModel import Operacion
from src.documento.factura.iva.ivaModel import iva
from src.detalleFactura.detalleFacturaModel import DetalleFactura
from src.producto.prodModel import Producto
from datetime import datetime


# Funciones para obtener documentos
def get_all_documentos(db: Session):
    return db.query(Documento).all()


def get_documento_by_id(db: Session, documento_id: int):
    return db.query(Documento).filter(Documento.id == documento_id).first()


def get_documento_by_numero_control(db: Session, numero_control: str):
    return (
        db.query(Documento).filter(Documento.numero_control == numero_control).first()
    )


def get_documentos_by_empresa_id(db: Session, empresa_id: int):
    return db.query(Documento).filter(Documento.empresa_id == empresa_id).all()


def get_documentos_by_cliente_id(db: Session, cliente_id: int):
    return db.query(Documento).filter(Documento.cliente_id == cliente_id).all()


# Funciones para crear documentos
# Estas funciones manejan la creación de documentos y sus relaciones con otros modelos
def get_or_create_factura(db: Session, documento_data: FacturaSchema):
    documento = (
        db.query(Documento)
        .filter(Documento.numero_control == documento_data.numero_control)
        .first()
    )

    try:
        if not documento:
            # Verificamos si existe la empresa
            empresa = get_empresa_by_id(db, documento_data.empresa_id)
            if not empresa:
                return {
                    "error": "La empresa_id no existe y es requerida para crear un documento."
                }

            # Verificamos si existe el cliente
            cliente = get_cliente_by_id(db, documento_data.cliente_id)
            if not cliente:
                return {
                    "error": "El cliente_id no existe y es requerido para crear un documento."
                }

            # Creamos el documento dependiendo del tipo
            if documento_data.tipo_documento == "Factura":
                # Crear la factura como parte de la tabla polimórfica Documento
                factura = Factura(
                    tipo_documento=documento_data.tipo_documento,
                    numero_control=documento_data.numero_control,
                    estado="Activo",  # Asignamos un estado por defecto
                    empresa_id=empresa.id,
                    cliente_id=cliente.id,
                    fecha_emision=datetime.today().date(),
                    hora_emision=datetime.now().time(),
                    monto_exento=documento_data.monto_exento,
                    total=documento_data.total,
                )

                # Guardar la factura en la base de datos
                db.add(factura)
                db.commit()

                # Refrescar la factura para obtener los datos actualizados
                db.refresh(factura)

                try:
                    # Crear operaciones e impuestos después de guardar la factura
                    if documento_data.operaciones:
                        operaciones = [
                            Operacion(factura_id=factura.id, **operacion_data)
                            for operacion_data in documento_data.operaciones
                        ]
                        for operacion in operaciones:
                            db.add(operacion)

                    if documento_data.impuestos:
                        impuestos = [
                            iva(factura_id=factura.id, **iva_data)
                            for iva_data in documento_data.impuestos
                        ]
                        for impuesto in impuestos:
                            db.add(impuesto)

                    # Crear detalles de factura
                    if documento_data.detalles_factura:
                        for detalle_data in documento_data.detalles_factura:
                            detalle_factura = (
                                db.query(DetalleFactura)
                                .filter(
                                    DetalleFactura.factura_id == factura.id,
                                    DetalleFactura.producto_id
                                    == detalle_data["producto_id"],
                                )
                                .first()
                            )
                            if not detalle_factura:
                                # Verificamos si existe la factura
                                if not factura:
                                    db.rollback()
                                    return {
                                        "error": "La factura_id no existe y es requerida para crear un detalle de factura."
                                    }

                                producto = (
                                    db.query(Producto)
                                    .filter(Producto.id == detalle_data["producto_id"])
                                    .first()
                                )
                                if not producto:
                                    db.rollback()
                                    return {
                                        "error": "El producto no existe y es requerido para crear un detalle de factura."
                                    }

                                if detalle_data["cantidad"] <= 0:
                                    db.rollback()
                                    return {"error": "La cantidad debe ser mayor a 0."}

                                # calcular el total
                                total = detalle_data["cantidad"] * producto.precio

                                detalle_factura = DetalleFactura(
                                    factura_id=factura.id,
                                    producto_id=detalle_data["producto_id"],
                                    cantidad=detalle_data["cantidad"],
                                    total=total,
                                )
                                db.add(detalle_factura)
                                db.commit()
                                db.refresh(detalle_factura)

                    db.commit()
                except Exception as e:
                    db.rollback()
                    return {
                        "error": f"Ocurrió un error al crear los detalles de la factura: {str(e)}"
                    }

                return factura
            else:
                return {"error": "El tipo de documento debe ser válido."}

        return {
            "error": "El documento ya existe con el mismo número de control.",
            "documento": documento,
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Ocurrió un error al crear el documento: {str(e)}"}


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