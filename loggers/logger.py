"""
logger.py
This module configures a custom logger for the application with rotating file handlers.

Features:
- Logs are stored in the 'logs' directory.
- Rotates log files when they reach 10 MB, keeping up to 5 backups.
- CustomFormatter adds additional fields like device, user, and IP to log entries.

Dependencies:
- os: For file system operations.
- logging: For logging functionality.
- logging.handlers.RotatingFileHandler: For rotating log files.
- datetime: For timestamping log entries.
- zoneinfo: For timezone management.

Functions:
- get_logger: Configures and returns a logger instance.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from zoneinfo import ZoneInfo

# Cambiar la zona horaria a UTC
TIMEZONE = "UTC"

# Crear la carpeta de logs, si no existe
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


class CustomFormatter(logging.Formatter):
    """
    Formateador personalizado que añade información extra si no se proporciona.
    Se espera que cada registro tenga los campos 'device', 'user', 'ip' y 'custom_func'.
    """

    HEADER_LOGGED = False  # Variable de clase para controlar si el encabezado ya se registró

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.default_time_format = "%Y-%m-%d %H:%M:%S"
        self.default_msec_format = "%s.%03d"

    def formatTime(self, record, datefmt=None):
        from datetime import datetime
        ct = datetime.fromtimestamp(record.created, ZoneInfo(TIMEZONE))
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime(self.default_time_format)
            s = "%s,%03d" % (t, record.msecs)
        return s

    def format(self, record):
        # Asegurarse de que asctime esté disponible
        if not hasattr(record, "asctime"):
            record.asctime = self.formatTime(record, self.datefmt)

        if not hasattr(record, "device"):
            record.device = "UnknownDevice"
        if not hasattr(record, "user"):
            record.user = "UnknownUser"
        if not hasattr(record, "ip"):
            record.ip = "UnknownIP"
        if not hasattr(record, "custom_func"):
            record.custom_func = record.funcName
        if not hasattr(record, "args"):
            record.args = "[]"
        if not hasattr(record, "kwargs"):
            record.kwargs = "{}"

        # Agregar encabezado si no se ha registrado
        if not CustomFormatter.HEADER_LOGGED:
            header = "Time                    | Level    | Device         | User           | IP             | Func           | Message"
            separator = "-" * len(header)
            with open(LOG_DIR + f"/{datetime.now(ZoneInfo(TIMEZONE)).strftime('%Y-%m-%d')}.log", "a") as log_file:
                log_file.write(f"{header}\n{separator}\n")
            CustomFormatter.HEADER_LOGGED = True

        # Formatear el registro como una fila de tabla sin sobrescribir record.msg
        formatted_msg = f"{record.asctime:<20} | {record.levelname:<8} | {record.device:<14} | {record.user:<14} | {record.ip:<14} | {record.custom_func:<14} | {record.getMessage()}"
        return formatted_msg


def get_logger(logger_name: str):
    """
    Configura un logger con RotatingFileHandler que rota los archivos cuando alcanzan 10 MB y guarda hasta 5 backups.
    El formato de cada registro es:
    Time: %(asctime)s | Level: %(levelname)s | Device: %(device)s | User: %(user)s | IP: %(ip)s | Func: %(custom_func)s | Msg: %(message)s
    """
    now_tz = datetime.now(ZoneInfo(TIMEZONE))
    date_str = now_tz.strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_str}.log")

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    format_str = "%(message)s"  # El mensaje ya incluye el formato de tabla
    formatter = CustomFormatter(format_str)
    formatter.converter = lambda *args: datetime.now(ZoneInfo(TIMEZONE)).timetuple()

    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    # Deshabilitar el log en la terminal
    logger.propagate = False

    return logger


# Configuración global del logger
app_logger = get_logger("app")
