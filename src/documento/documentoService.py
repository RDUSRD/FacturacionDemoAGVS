from sqlalchemy.orm import Session
from src.documento.docModel import Documento
from src.documento.documentoSchema import DocumentoSchema, DocumentoUpdateSchema
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


def get_all_documentos(db: Session):
    return db.query(Documento).all()


def get_documento_by_id(db: Session, documento_id: int):
    return db.query(Documento).filter(Documento.id == documento_id).first()


def get_or_create_documento(db: Session, documento_data: DocumentoSchema):
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
                                    DetalleFactura.producto_id == detalle_data["producto_id"],
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

                                producto = db.query(Producto).filter(Producto.id == detalle_data["producto_id"]).first()
                                if not producto:
                                    db.rollback()
                                    return {
                                        "error": "La producto_id no existe y es requerida para crear un detalle de factura."
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
                    return {"error": f"Ocurrió un error al crear los detalles de la factura: {str(e)}"}

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


def update_documento(
    db: Session, documento_id: int, documento_data: DocumentoUpdateSchema
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        return {"error": "El documento con el ID especificado no existe."}

    if documento_data.empresa_id:
        # Verificamos si la empresa_id ha cambiado
        if documento.empresa_id != documento_data.empresa_id:
            # Verificamos si existe la nueva empresa
            empresa = get_empresa_by_id(db, documento_data.empresa_id)
            if not empresa:
                return {
                    "error": "La empresa_id no existe y es requerida para actualizar el documento."
                }
            documento.empresa_id = empresa.id
    if documento_data.cliente_id:
        # Verificamos si la cliente_id ha cambiado
        if documento.cliente_id != documento_data.cliente_id:
            # Verificamos si existe el nuevo cliente
            cliente = get_cliente_by_id(db, documento_data.cliente_id)
            if not cliente:
                return {
                    "error": "El cliente_id no existe y es requerido para actualizar el documento."
                }
            documento.cliente_id = cliente.id

    # Actualizamos el tipo de documento si es necesario
    if documento_data.tipo_documento:
        if documento_data.tipo_documento == "factura":
            documento = Factura(
                monto_exento=documento_data.monto_exento, total=documento_data.total
            )
            # Actualizar operaciones asociadas
            if documento_data.operaciones:
                for operacion_data in documento_data.operaciones:
                    operacion = Operacion(**operacion_data)
                    operacion.factura = documento
                    db.add(operacion)

            # Actualizar impuestos asociados
            if documento_data.impuestos:
                for iva_data in documento_data.impuestos:
                    iva_aux = iva(**iva_data)
                    iva_aux.factura = documento
                    db.add(iva_aux)
        elif documento_data.tipo_documento == "OrdenEntrega":
            documento = OrdenEntrega(**documento_data.model_dump(exclude_unset=True))
        elif documento_data.tipo_documento == "notaCredito":
            documento = NotaCredito(**documento_data.model_dump(exclude_unset=True))
        elif documento_data.tipo_documento == "notaDebito":
            documento = NotaDebito(**documento_data.model_dump(exclude_unset=True))
        else:
            return {"error": "El tipo de documento debe ser válido."}

    for key, value in documento_data.model_dump(exclude_unset=True).items():
        setattr(documento, key, value)
    db.commit()
    db.refresh(documento)
    return documento
