from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from src.monedas.dolar.dolarService import obtener_dolar_bcv
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("MonedaRouter")

router = APIRouter(prefix="/moneda", tags=["Moneda"])


@router.get("/dolar/obtener")
def obtener_dolar(request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info("Obteniendo el registro único del dólar", extra=request_info)
    try:
        registro = obtener_dolar_bcv(db)
        if "error" in registro:
            raise HTTPException(status_code=400, detail=registro["error"])
        return registro
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
