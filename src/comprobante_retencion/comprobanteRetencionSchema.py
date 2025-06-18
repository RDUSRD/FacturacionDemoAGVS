from pydantic import BaseModel, Field

class ComprobanteRetencionSchema(BaseModel):
    id: int
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido")
    tipo_impuesto: str = Field(..., description="Debe especificar el tipo de impuesto")
    monto_retenido: float = Field(..., ge=0, description="El monto retenido debe ser mayor o igual a 0")

    class Config:
        orm_mode = True
