from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.monedas.dolar.dolarService import obtener_dolar_bcv

router = APIRouter(prefix="/moneda", tags=["Moneda"])


@router.get("/dolar/obtener")
def obtener_dolar(db: Session = Depends(get_db)):
    """
    Endpoint para obtener el registro único del dólar.
    """
    try:
        registro = obtener_dolar_bcv(db)
        if "error" in registro:
            raise HTTPException(status_code=400, detail=registro["error"])
        return registro
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
