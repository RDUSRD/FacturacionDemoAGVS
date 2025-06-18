from pydantic import BaseModel, Field
from typing import List

class NotaDebitoSchema(BaseModel):
    id: int
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido")
    operaciones: List[dict] = Field(..., description="Debe especificar las operaciones de la nota de débito")
    montos_base_iva: List[dict] = Field(..., description="Debe especificar los montos base para IVA")
    monto_exento: float = Field(..., ge=0, description="El monto exento debe ser mayor o igual a 0")
    montos_iva: List[dict] = Field(..., description="Debe especificar los montos de IVA")
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0")

    class Config:
        orm_mode = True

class NotaCreditoSchema(BaseModel):
    id: int
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido")
    operaciones: List[dict] = Field(..., description="Debe especificar las operaciones de la nota de crédito")
    montos_base_iva: List[dict] = Field(..., description="Debe especificar los montos base para IVA")
    monto_exento: float = Field(..., ge=0, description="El monto exento debe ser mayor o igual a 0")
    montos_iva: List[dict] = Field(..., description="Debe especificar los montos de IVA")
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0")

    class Config:
        orm_mode = True
