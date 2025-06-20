from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.documentoService import (
    get_documento_by_id,
    get_all_documentos,
    get_or_create_documento,
    update_documento,
)
from src.documento.documentoSchema import (
    FacturaSchema,
    OrdenEntregaSchema,
    NotaCreditoSchema,
    NotaDebitoSchema,
)

router = APIRouter(prefix="/documento", tags=["Documento"])


@router.get("/")
def get_documentos(db: Session = Depends(get_db)):
    return get_all_documentos(db)


@router.get("/{documento_id}")
def get_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = get_documento_by_id(db, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


@router.post("/create/factura")
def create_factura_endpoint(factura_data: FacturaSchema, db: Session = Depends(get_db)):
    return get_or_create_documento(db, factura_data)


@router.post("/create/orden-entrega")
def create_orden_entrega_endpoint(
    orden_entrega_data: OrdenEntregaSchema, db: Session = Depends(get_db)
):
    return get_or_create_documento(db, orden_entrega_data)


@router.post("/create/nota-credito")
def create_nota_credito_endpoint(
    nota_credito_data: NotaCreditoSchema, db: Session = Depends(get_db)
):
    return get_or_create_documento(db, nota_credito_data)


@router.post("/create/nota-debito")
def create_nota_debito_endpoint(
    nota_debito_data: NotaDebitoSchema, db: Session = Depends(get_db)
):
    return get_or_create_documento(db, nota_debito_data)


@router.put("/update/factura/{documento_id}")
def update_factura_endpoint(
    documento_id: int,
    factura_data: FacturaSchema,
    db: Session = Depends(get_db),
):
    documento = update_documento(db, documento_id, factura_data)
    if not documento:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return documento


@router.put("/update/orden-entrega/{documento_id}")
def update_orden_entrega_endpoint(
    documento_id: int,
    orden_entrega_data: OrdenEntregaSchema,
    db: Session = Depends(get_db),
):
    documento = update_documento(db, documento_id, orden_entrega_data)
    if not documento:
        raise HTTPException(status_code=404, detail="Orden de entrega no encontrada")
    return documento


@router.put("/update/nota-credito/{documento_id}")
def update_nota_credito_endpoint(
    documento_id: int,
    nota_credito_data: NotaCreditoSchema,
    db: Session = Depends(get_db),
):
    documento = update_documento(db, documento_id, nota_credito_data)
    if not documento:
        raise HTTPException(status_code=404, detail="Nota de crédito no encontrada")
    return documento


@router.put("/update/nota-debito/{documento_id}")
def update_nota_debito_endpoint(
    documento_id: int,
    nota_debito_data: NotaDebitoSchema,
    db: Session = Depends(get_db),
):
    documento = update_documento(db, documento_id, nota_debito_data)
    if not documento:
        raise HTTPException(status_code=404, detail="Nota de débito no encontrada")
    return documento
