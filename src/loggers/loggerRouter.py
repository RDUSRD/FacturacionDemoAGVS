from fastapi import APIRouter, Request, Query
import os
from src.loggers.loggerService import convert_logs_to_json, get_logger, get_request_info
from datetime import datetime

logger = get_logger("LoggerRouter")
router = APIRouter(prefix="/logger", tags=["Logger"])


@router.get("/logs/today")
def get_logs_today(request: Request, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    request_info = get_request_info(request)
    logger.info("Obteniendo logs del día actual", extra=request_info)
    today_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = f"logs/{today_date}.log"

    if not os.path.exists(log_file_path):
        return {"error": "Archivo de logs no encontrado para el día actual"}

    logs = convert_logs_to_json(log_file_path, limit=limit, offset=offset)
    return logs


@router.get("/logs/{date}")
def get_logs_by_date(date: str, request: Request, limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo logs para la fecha: {date}", extra=request_info)
    try:
        datetime.strptime(date, "%Y-%m-%d")  # Validar el formato de la fecha
    except ValueError:
        return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}

    log_file_path = f"logs/{date}.log"

    if not os.path.exists(log_file_path):
        return {"error": f"Archivo de logs no encontrado para la fecha {date}"}

    logs = convert_logs_to_json(log_file_path, limit=limit, offset=offset)
    return logs
