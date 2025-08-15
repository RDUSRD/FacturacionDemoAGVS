from sqlalchemy.orm import Session
from src.documento.docModel import Documento
from src.documento.factura.facModel import Factura
from src.documento.notas.notaModel import NotaCredito, NotaDebito
from src.documento.factura.iva.ivaModel import iva


# Función para obtener todos los documentos con el ID relacionado
def get_all_documentos(db: Session):
    documentos = db.query(Documento).all()
    documentos_enriquecidos = []

    for documento in documentos:
        documento_dict = documento.__dict__.copy()

        if documento.tipo_documento == "Factura":
            factura = db.query(Factura).filter(Factura.id == documento.id).first()
            documento_dict["factura_id"] = factura.factura_id if factura else None
            documento_dict["impuestos"] = db.query(iva).filter(iva.factura_id == documento.id).all()

        elif documento.tipo_documento == "NotaCredito":
            nota_credito = db.query(NotaCredito).filter(NotaCredito.id == documento.id).first()
            documento_dict["nota_credito_id"] = nota_credito.nota_credito_id if nota_credito else None

        elif documento.tipo_documento == "NotaDebito":
            nota_debito = db.query(NotaDebito).filter(NotaDebito.id == documento.id).first()
            documento_dict["nota_debito_id"] = nota_debito.nota_debito_id if nota_debito else None

        documentos_enriquecidos.append(documento_dict)

    return documentos_enriquecidos


# Función para obtener un documento por ID
def get_documento_by_id(db: Session, documento_id: int):
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if documento:
        documento_dict = documento.__dict__.copy()

        if documento.tipo_documento == "Factura":
            factura = db.query(Factura).filter(Factura.id == documento.id).first()
            documento_dict["factura_id"] = factura.factura_id if factura else None
            documento_dict["impuestos"] = db.query(iva).filter(iva.factura_id == documento.id).all()

        elif documento.tipo_documento == "NotaCredito":
            nota_credito = db.query(NotaCredito).filter(NotaCredito.id == documento.id).first()
            documento_dict["nota_credito_id"] = nota_credito.nota_credito_id if nota_credito else None

        elif documento.tipo_documento == "NotaDebito":
            nota_debito = db.query(NotaDebito).filter(NotaDebito.id == documento.id).first()
            documento_dict["nota_debito_id"] = nota_debito.nota_debito_id if nota_debito else None

        return documento_dict
    return None


# Función para obtener un documento por número de control
def get_documento_by_numero_control(db: Session, numero_control: str):
    documento = db.query(Documento).filter(Documento.numero_control == numero_control).first()
    if documento:
        documento_dict = documento.__dict__.copy()

        if documento.tipo_documento == "Factura":
            factura = db.query(Factura).filter(Factura.id == documento.id).first()
            documento_dict["factura_id"] = factura.factura_id if factura else None
            documento_dict["impuestos"] = db.query(iva).filter(iva.factura_id == documento.id).all()

        elif documento.tipo_documento == "NotaCredito":
            nota_credito = db.query(NotaCredito).filter(NotaCredito.id == documento.id).first()
            documento_dict["nota_credito_id"] = nota_credito.nota_credito_id if nota_credito else None

        elif documento.tipo_documento == "NotaDebito":
            nota_debito = db.query(NotaDebito).filter(NotaDebito.id == documento.id).first()
            documento_dict["nota_debito_id"] = nota_debito.nota_debito_id if nota_debito else None

        return documento_dict
    return None


# Función para obtener documentos por ID de empresa
def get_documentos_by_empresa_id(db: Session, empresa_id: int):
    documentos = db.query(Documento).filter(Documento.empresa_id == empresa_id).all()
    documentos_enriquecidos = []

    for documento in documentos:
        documento_dict = documento.__dict__.copy()

        if documento.tipo_documento == "Factura":
            factura = db.query(Factura).filter(Factura.id == documento.id).first()
            documento_dict["factura_id"] = factura.factura_id if factura else None
            documento_dict["impuestos"] = db.query(iva).filter(iva.factura_id == documento.id).all()

        elif documento.tipo_documento == "NotaCredito":
            nota_credito = db.query(NotaCredito).filter(NotaCredito.id == documento.id).first()
            documento_dict["nota_credito_id"] = nota_credito.nota_credito_id if nota_credito else None

        elif documento.tipo_documento == "NotaDebito":
            nota_debito = db.query(NotaDebito).filter(NotaDebito.id == documento.id).first()
            documento_dict["nota_debito_id"] = nota_debito.nota_debito_id if nota_debito else None

        documentos_enriquecidos.append(documento_dict)

    return documentos_enriquecidos


# Función para obtener documentos por ID de cliente
def get_documentos_by_cliente_id(db: Session, cliente_id: int):
    documentos = db.query(Documento).filter(Documento.cliente_id == cliente_id).all()
    documentos_enriquecidos = []

    for documento in documentos:
        documento_dict = documento.__dict__.copy()

        if documento.tipo_documento == "Factura":
            factura = db.query(Factura).filter(Factura.id == documento.id).first()
            documento_dict["factura_id"] = factura.factura_id if factura else None
            documento_dict["impuestos"] = db.query(iva).filter(iva.factura_id == documento.id).all()

        elif documento.tipo_documento == "NotaCredito":
            nota_credito = db.query(NotaCredito).filter(NotaCredito.id == documento.id).first()
            documento_dict["nota_credito_id"] = nota_credito.nota_credito_id if nota_credito else None

        elif documento.tipo_documento == "NotaDebito":
            nota_debito = db.query(NotaDebito).filter(NotaDebito.id == documento.id).first()
            documento_dict["nota_debito_id"] = nota_debito.nota_debito_id if nota_debito else None

        documentos_enriquecidos.append(documento_dict)

    return documentos_enriquecidos
