from fastapi import APIRouter
import os
from src.loggers.loggerService import convert_logs_to_json
from datetime import datetime

router = APIRouter(prefix="/logger", tags=["Logger"])


@router.get("/logs/today")
def get_logs_today():
    """
    Endpoint para obtener los logs del día actual.
    """
    today_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = f"logs/{today_date}.log"

    if not os.path.exists(log_file_path):
        return {"error": "Archivo de logs no encontrado para el día actual"}

    logs = convert_logs_to_json(log_file_path)
    return logs


@router.get("/logs/{date}")
def get_logs_by_date(date: str):
    """
    Endpoint para obtener los logs de una fecha específica.

    Args:
        date (str): Fecha en formato YYYY-MM-DD.

    Returns:
        list: Lista de logs en formato JSON o un mensaje de error si no se encuentra el archivo.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")  # Validar el formato de la fecha
    except ValueError:
        return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}

    log_file_path = f"logs/{date}.log"

    if not os.path.exists(log_file_path):
        return {"error": f"Archivo de logs no encontrado para la fecha {date}"}

    logs = convert_logs_to_json(log_file_path)
    return logs
