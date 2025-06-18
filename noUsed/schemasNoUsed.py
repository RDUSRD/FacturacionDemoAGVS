"""
schemas.py
Este archivo define los esquemas Pydantic para validación de solicitudes y serialización de respuestas.

Dependencias:
- pydantic: Para validación y serialización de datos.
- datetime: Para campos de fecha y hora.
- typing: Para anotaciones de tipo.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

# DigitalPrinterBase: Esquema para los datos de la imprenta digital.
class DigitalPrinterBase(BaseModel):
    id: int
    name: str
    rif: str
    control_number_start: int
    control_number_end: int
    current_control_number: int
    authorization_nomenclature: str
    authorization_date: datetime

# DocumentResponse: Esquema de respuesta al retornar datos de un documento.
class DocumentResponse(BaseModel):
    id: int
    document_type: str
    document_number: int
    emisor: Dict[str, str]  # Simplificado para representar datos básicos
    receptor: Dict[str, str]  # Simplificado para representar datos básicos
    issuance_date: datetime
    issuance_time: str
    control_number: int
    digital_printer: DigitalPrinterBase
    status: str

    class Config:
        orm_mode = True

# AuditLogSchema: Esquema para registrar datos de auditoría.
class AuditLogSchema(BaseModel):
    id: int
    transaction_type: str
    transaction_data: Dict
    transaction_date: datetime
    client_ip: str

    class Config:
        orm_mode = True