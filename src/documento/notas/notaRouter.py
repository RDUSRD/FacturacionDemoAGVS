from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.documento.notas.notaService import (
    get_nota_debito_by_id,
    get_all_notas_debito,
    get_nota_credito_by_id,
    get_all_notas_credito,
)

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
