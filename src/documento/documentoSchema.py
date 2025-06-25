from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional


class DocumentoSchema(BaseModel):
    tipo_documento: str = Field(
        ..., description="Debe especificar el tipo de documento", example="Factura"
    )

    fecha_emision: Optional[date] = Field(
        None, description="La fecha de emisión debe ser válida", example="2025-06-20"
    )
    hora_emision: Optional[time] = Field(
        None, description="La hora de emisión debe ser válida", example="14:30:00"
    )
    empresa_id: int = Field(
        ..., ge=1, description="El ID de la empresa debe ser válido", example=1
    )
    cliente_id: int = Field(
        ..., ge=1, description="El ID del cliente debe ser válido", example=2
    )

    class Config:
        from_attributes = True


class DocumentoUpdateSchema(BaseModel):
    tipo_documento: Optional[str] = Field(
        None, description="Debe especificar el tipo de documento", example="Factura"
    )
    numero_control: Optional[str] = Field(
        None,
        pattern=r"^\d{8}$",
        description="El número de control debe tener 8 dígitos",
        example="12345678",
    )
    fecha_emision: Optional[date] = Field(
        None, description="La fecha de emisión debe ser válida", example="2025-06-20"
    )
    hora_emision: Optional[time] = Field(
        None, description="La hora de emisión debe ser válida", example="14:30:00"
    )
    empresa_id: Optional[int] = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=1
    )
    cliente_id: Optional[int] = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=2
    )
    estado: Optional[str] = Field(
        None, description="Debe especificar el estado del documento", example="Activo"
    )

    class Config:
        from_attributes = True
