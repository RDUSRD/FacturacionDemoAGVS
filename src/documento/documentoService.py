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
                return {"error": "La empresa_id no existe y es requerida para crear un documento."}

            # Verificamos si existe el cliente
            cliente = get_cliente_by_id(db, documento_data.cliente_id)
            if not cliente:
                return {"error": "El cliente_id no existe y es requerido para crear un documento."}

            # Creamos el documento dependiendo del tipo
            if documento_data.tipo_documento == "Factura":
                if not documento_data.operaciones or len(documento_data.operaciones) == 0:
                    return {"error": "El campo 'operaciones' es obligatorio y no puede ser nulo o vacío."}

                # Crear operaciones asociadas
                operaciones = [Operacion(**operacion_data) for operacion_data in documento_data.operaciones]
                for operacion in operaciones:
                    db.add(operacion)

                # Crear impuestos asociados
                impuestos = [iva(**iva_data) for iva_data in documento_data.impuestos]
                for impuesto in impuestos:
                    db.add(impuesto)

                # Crear la factura
                factura = Factura(
                    monto_exento=documento_data.monto_exento,
                    total=documento_data.total
                )
                db.add(factura)
                db.commit()

                # Guardar las relaciones de operaciones e impuestos en la base de datos
                for operacion in operaciones:
                    db.add(operacion)
                for impuesto in impuestos:
                    db.add(impuesto)

                db.commit()

                # Asegurarse de que el objeto documento se mantenga correctamente
                db.refresh(factura)
                documento = factura
            elif documento_data.tipo_documento == "OrdenEntrega":
                documento = OrdenEntrega(**documento_data.model_dump())
            elif documento_data.tipo_documento == "notaCredito":
                documento = NotaCredito(**documento_data.model_dump())
            elif documento_data.tipo_documento == "notaDebito":
                documento = NotaDebito(**documento_data.model_dump())
            else:
                return {"error": "El tipo de documento debe ser válido."}

            # Validamos y asignamos los campos obligatorios antes de agregar el documento
            if not documento_data.numero_control:
                return {"error": "El campo 'numero_control' es obligatorio y no puede ser nulo."}
            if not empresa:
                return {"error": "El campo 'empresa_id' es obligatorio y no puede ser nulo."}
            if not cliente:
                return {"error": "El campo 'cliente_id' es obligatorio y no puede ser nulo."}

            # Crear el objeto Documento con los argumentos proporcionados
            documento = Documento(
                tipo_documento=documento_data.tipo_documento,
                numero_control=documento_data.numero_control,
                estado="Activo",  # Asignamos un estado por defecto
                empresa_id=empresa.id,
                cliente_id=cliente.id,
                fecha_emision=datetime.today().date(),
                hora_emision=datetime.now().time()
            )

            db.add(documento)
            db.commit()
            db.refresh(documento)
            return documento
        return {"error": "El documento ya existe con el mismo número de control.", "documento": documento}
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
                return {"error": "La empresa_id no existe y es requerida para actualizar el documento."}
            documento.empresa_id = empresa.id
    if documento_data.cliente_id:
        # Verificamos si la cliente_id ha cambiado
        if documento.cliente_id != documento_data.cliente_id:
            # Verificamos si existe el nuevo cliente
            cliente = get_cliente_by_id(db, documento_data.cliente_id)
            if not cliente:
                return {"error": "El cliente_id no existe y es requerido para actualizar el documento."}
            documento.cliente_id = cliente.id

    # Actualizamos el tipo de documento si es necesario
    if documento_data.tipo_documento:
        if documento_data.tipo_documento == "factura":
            documento = Factura(
                monto_exento=documento_data.monto_exento,
                total=documento_data.total
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
