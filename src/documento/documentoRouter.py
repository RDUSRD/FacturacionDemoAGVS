from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.documentoService import (
    get_documento_by_id,
    get_all_documentos,
    get_documento_by_numero_control,
    get_documentos_by_empresa_id,
    get_documentos_by_cliente_id,
    get_or_create_factura,
    get_or_create_nota_credito,
    get_or_create_nota_debito,
    get_or_create_orden_entrega,
)
from src.documento.factura.facturaSchema import FacturaSchema
from src.documento.orden_entrega.ordenEntregaSchema import OrdenEntregaSchema
from src.documento.notas.notaSchema import (
    NotaCreditoSchema,
    NotaDebitoSchema,
)


router = APIRouter(prefix="/documento", tags=["Documento"])


# Endpoints para obtener documentos
@router.get("/")
def get_documentos(db: Session = Depends(get_db)):
    return get_all_documentos(db)


@router.get("/{documento_id}")
def get_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = get_documento_by_id(db, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


@router.get("/numero-control/{numero_control}")
def get_documento_numero_control(numero_control: str, db: Session = Depends(get_db)):
    documento = get_documento_by_numero_control(db, numero_control)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


@router.get("/empresa/{empresa_id}")
def get_documentos_empresa_id(empresa_id: int, db: Session = Depends(get_db)):
    documentos = get_documentos_by_empresa_id(db, empresa_id)
    if not documentos:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron documentos para la empresa especificada",
        )
    return documentos


@router.get("/cliente/{cliente_id}")
def get_documentos_cliente_id(cliente_id: int, db: Session = Depends(get_db)):
    documentos = get_documentos_by_cliente_id(db, cliente_id)
    if not documentos:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron documentos para el cliente especificado",
        )
    return documentos


# Endpoints para crear documentos
@router.post("/create/factura")
def create_factura_endpoint(factura_data: FacturaSchema, db: Session = Depends(get_db)):
    return get_or_create_factura(db, factura_data)


@router.post("/create/orden-entrega")
def create_orden_entrega_endpoint(
    orden_entrega_data: OrdenEntregaSchema, db: Session = Depends(get_db)
):
    return get_or_create_orden_entrega(db, orden_entrega_data)


@router.post("/create/nota-credito")
def create_nota_credito_endpoint(
    nota_credito_data: NotaCreditoSchema, db: Session = Depends(get_db)
):
    return get_or_create_nota_credito(db, nota_credito_data)


@router.post("/create/nota-debito")
def create_nota_debito_endpoint(
    nota_debito_data: NotaDebitoSchema, db: Session = Depends(get_db)
):
    return get_or_create_nota_debito(db, nota_debito_data)
