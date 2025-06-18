from pydantic import BaseModel, Field
from typing import List

class FacturaSchema(BaseModel):
    id: int
    operaciones: List[dict] = Field(..., description="Debe especificar las operaciones de la factura")
    montos_base_iva: List[dict] = Field(..., description="Debe especificar los montos base para IVA")
    monto_exento: float = Field(..., ge=0, description="El monto exento debe ser mayor o igual a 0")
    montos_iva: List[dict] = Field(..., description="Debe especificar los montos de IVA")
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0")

    class Config:
        orm_mode = True
