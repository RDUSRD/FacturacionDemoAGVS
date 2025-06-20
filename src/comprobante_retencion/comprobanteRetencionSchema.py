from pydantic import BaseModel, Field
from typing import Optional

class ComprobanteRetencionSchema(BaseModel):
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    tipo_impuesto: str = Field(..., description="Debe especificar el tipo de impuesto", example="IVA")
    monto_retenido: float = Field(..., ge=0, description="El monto retenido debe ser mayor o igual a 0", example=16.0)

    class Config:
        from_attributes = True

class ComprobanteRetencionUpdateSchema(BaseModel):
    documento_relacionado_id: Optional[int] = Field(None, ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    tipo_impuesto: Optional[str] = Field(None, description="Debe especificar el tipo de impuesto", example="IVA")
    monto_retenido: Optional[float] = Field(None, ge=0, description="El monto retenido debe ser mayor o igual a 0", example=16.0)

    class Config:
        from_attributes = True
