from pydantic import BaseModel, Field
from datetime import datetime

class AuditoriaSchema(BaseModel):
    id: int
    tabla_afectada: str = Field(..., description="Debe especificar la tabla afectada")
    registro_id: int = Field(..., ge=1, description="El ID del registro debe ser válido")
    accion: str = Field(..., description="Debe especificar la acción realizada")
    detalles: str = Field(None, description="Detalles adicionales de la acción")
    fecha_hora: datetime = Field(..., description="Debe especificar la fecha y hora de la acción")
    usuario: str = Field(..., description="Debe especificar el usuario que realizó la acción")

    class Config:
        orm_mode = True
