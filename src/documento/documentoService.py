from sqlalchemy.orm import Session
from src.documento.docModel import Documento
from src.documento.documentoSchema import DocumentoSchema, DocumentoUpdateSchema
from src.empresa.empresaService import get_empresa_by_id
from src.cliente.clienteService import get_cliente_by_id


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
    if not documento:
        # Verificamos si existe la empresa
        empresa = get_empresa_by_id(db, documento_data.empresa_id)
        if not empresa:
            raise ValueError("La empresa_id es requerida para crear un documento.")
        
        # Verificamos si el tipo de documento es válido
        if documento_data.tipo_documento not in ["Factura", "OrdenEntrega"]:
            raise ValueError("El tipo de documento debe ser 'Factura' o 'OrdenEntrega'.")
        
        # Verificamos si existe el cliente
        cliente = get_cliente_by_id(db, documento_data.cliente_id)
        if not cliente:
            raise ValueError("El cliente_id es requerido para crear un documento.")
        
        # Creamos el documento
        documento = Documento(**documento_data.model_dump())
        documento.empresa_id = empresa.id
        documento.cliente_id = cliente.id
        db.add(documento)
        db.commit()
        db.refresh(documento)
    return documento


def update_documento(
    db: Session, documento_id: int, documento_data: DocumentoUpdateSchema
):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if documento:
        
        # Verificamos si existe la empresa
        empresa = get_empresa_by_id(db, documento_data.empresa_id)
        if not empresa:
            raise ValueError("La empresa_id es requerida para crear un documento.")
        
        # Verificamos si existe el cliente
        cliente = get_cliente_by_id(db, documento_data.cliente_id)
        if not cliente:
            raise ValueError("El cliente_id es requerido para crear un documento.")
        
        # Actualizamos los campos del documento
        documento.empresa_id = empresa.id
        documento.cliente_id = cliente.id
        
        for key, value in documento_data.model_dump(exclude_unset=True).items():
            setattr(documento, key, value)
        db.commit()
        db.refresh(documento)
    return documento


# def delete_documento(db: Session, documento_id: int):
#     documento = db.query(Documento).filter(Documento.id == documento_id).first()
#     if documento:
#         db.delete(documento)
#         db.commit()
#     return documento
