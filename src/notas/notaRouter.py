from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.notas.notaService import (
    get_nota_debito_by_id,
    get_all_notas_debito,
    get_or_create_nota_debito,
    update_nota_debito,
    # delete_nota_debito,
    get_nota_credito_by_id,
    get_all_notas_credito,
    get_or_create_nota_credito,
    update_nota_credito,
    # delete_nota_credito,
)
from src.notas.notaSchema import NotaDebitoSchema, NotaDebitoUpdateSchema, NotaCreditoSchema, NotaCreditoUpdateSchema

router = APIRouter(prefix="/notas", tags=["Notas"])

# Rutas para Notas de Débito
@router.get("/nota_debito")
def get_notas_debito(db: Session = Depends(get_db)):
    return get_all_notas_debito(db)

@router.get("/nota_debito/{nota_debito_id}")
def get_nota_debito(nota_debito_id: int, db: Session = Depends(get_db)):
    nota_debito = get_nota_debito_by_id(db, nota_debito_id)
    if not nota_debito:
        raise HTTPException(status_code=404, detail="Nota de débito no encontrada")
    return nota_debito

@router.post("/nota_debito")
def create_or_get_nota_debito_endpoint(nota_debito_data: NotaDebitoSchema, db: Session = Depends(get_db)):
    return get_or_create_nota_debito(db, nota_debito_data)

@router.put("/nota_debito/{nota_debito_id}")
def update_nota_debito_endpoint(nota_debito_id: int, nota_debito_data: NotaDebitoUpdateSchema, db: Session = Depends(get_db)):
    nota_debito = update_nota_debito(db, nota_debito_id, nota_debito_data)
    if not nota_debito:
        raise HTTPException(status_code=404, detail="Nota de débito no encontrada")
    return nota_debito

# @router.delete("/nota_debito/{nota_debito_id}")
# def delete_nota_debito_endpoint(nota_debito_id: int, db: Session = Depends(get_db)):
#     nota_debito = delete_nota_debito(db, nota_debito_id)
#     if not nota_debito:
#         raise HTTPException(status_code=404, detail="Nota de débito no encontrada")
#     return {"detail": "Nota de débito eliminada correctamente"}


# Rutas para Notas de Crédito
@router.get("/nota_credito")
def get_notas_credito(db: Session = Depends(get_db)):
    return get_all_notas_credito(db)

@router.get("/nota_credito/{nota_credito_id}")
def get_nota_credito(nota_credito_id: int, db: Session = Depends(get_db)):
    nota_credito = get_nota_credito_by_id(db, nota_credito_id)
    if not nota_credito:
        raise HTTPException(status_code=404, detail="Nota de crédito no encontrada")
    return nota_credito

@router.post("/nota_credito")
def create_or_get_nota_credito_endpoint(nota_credito_data: NotaCreditoSchema, db: Session = Depends(get_db)):
    return get_or_create_nota_credito(db, nota_credito_data)

@router.put("/nota_credito/{nota_credito_id}")
def update_nota_credito_endpoint(nota_credito_id: int, nota_credito_data: NotaCreditoUpdateSchema, db: Session = Depends(get_db)):
    nota_credito = update_nota_credito(db, nota_credito_id, nota_credito_data)
    if not nota_credito:
        raise HTTPException(status_code=404, detail="Nota de crédito no encontrada")
    return nota_credito

# @router.delete("/nota_credito/{nota_credito_id}")
# def delete_nota_credito_endpoint(nota_credito_id: int, db: Session = Depends(get_db)):
#     nota_credito = delete_nota_credito(db, nota_credito_id)
#     if not nota_credito:
#         raise HTTPException(status_code=404, detail="Nota de crédito no encontrada")
#     return {"detail": "Nota de crédito eliminada correctamente"}
