from pydantic import BaseModel, Field
from datetime import date, time

class DocumentoSchema(BaseModel):
    id: int
    tipo_documento: str = Field(..., description="Debe especificar el tipo de documento")
    numero_control: str = Field(..., regex=r"^\d{8}$", description="El número de control debe tener 8 dígitos")
    fecha_emision: date = Field(..., description="La fecha de emisión debe ser válida")
    hora_emision: time = Field(..., description="La hora de emisión debe ser válida")
    empresa_id: int = Field(..., ge=1, description="El ID de la empresa debe ser válido")
    cliente_id: int = Field(..., ge=1, description="El ID del cliente debe ser válido")
    estado: str = Field(..., description="Debe especificar el estado del documento")

    class Config:
        orm_mode = True
