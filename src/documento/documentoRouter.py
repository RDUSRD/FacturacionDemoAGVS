from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.documentoService import (
    get_documento_by_id,
    get_all_documentos,
    get_or_create_documento,
    update_documento,
    # delete_documento,
)
from src.documento.documentoSchema import DocumentoSchema, DocumentoUpdateSchema

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


@router.post("/create")
def create_documento_endpoint(
    documento_data: DocumentoSchema, db: Session = Depends(get_db)
):
    return get_or_create_documento(db, documento_data)


@router.put("/{documento_id}")
def update_documento_endpoint(
    documento_id: int,
    documento_data: DocumentoUpdateSchema,
    db: Session = Depends(get_db),
):
    documento = update_documento(db, documento_id, documento_data)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return documento


# @router.delete("/{documento_id}")
# def delete_documento_endpoint(documento_id: int, db: Session = Depends(get_db)):
#     documento = delete_documento(db, documento_id)
#     if not documento:
#         raise HTTPException(status_code=404, detail="Documento no encontrado")
#     return {"detail": "Documento eliminado correctamente"}
