from pydantic import BaseModel, Field
from typing import List, Optional

class NotaDebitoSchema(BaseModel):
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    operaciones: List[dict] = Field(..., description="Debe especificar las operaciones de la nota de débito", example=[{"operacion": "compra", "monto": 100.0}])
    montos_base_iva: List[dict] = Field(..., description="Debe especificar los montos base para IVA", example=[{"base": 100.0, "iva": 16.0}])
    monto_exento: float = Field(..., ge=0, description="El monto exento debe ser mayor o igual a 0", example=0.0)
    montos_iva: List[dict] = Field(..., description="Debe especificar los montos de IVA", example=[{"base": 100.0, "iva": 16.0}])
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0", example=116.0)

    class Config:
        from_attributes = True

class NotaDebitoUpdateSchema(BaseModel):
    documento_relacionado_id: Optional[int] = Field(None, ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    operaciones: Optional[List[dict]] = Field(None, description="Debe especificar las operaciones de la nota de débito", example=[{"operacion": "compra", "monto": 100.0}])
    montos_base_iva: Optional[List[dict]] = Field(None, description="Debe especificar los montos base para IVA", example=[{"base": 100.0, "iva": 16.0}])
    monto_exento: Optional[float] = Field(None, ge=0, description="El monto exento debe ser mayor o igual a 0", example=0.0)
    montos_iva: Optional[List[dict]] = Field(None, description="Debe especificar los montos de IVA", example=[{"base": 100.0, "iva": 16.0}])
    total: Optional[float] = Field(None, ge=0, description="El total debe ser mayor o igual a 0", example=116.0)

    class Config:
        from_attributes = True

class NotaCreditoSchema(BaseModel):
    documento_relacionado_id: int = Field(..., ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    operaciones: List[dict] = Field(..., description="Debe especificar las operaciones de la nota de crédito", example=[{"operacion": "compra", "monto": 100.0}])
    montos_base_iva: List[dict] = Field(..., description="Debe especificar los montos base para IVA", example=[{"base": 100.0, "iva": 16.0}])
    monto_exento: float = Field(..., ge=0, description="El monto exento debe ser mayor o igual a 0", example=0.0)
    montos_iva: List[dict] = Field(..., description="Debe especificar los montos de IVA", example=[{"base": 100.0, "iva": 16.0}])
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0", example=116.0)

    class Config:
        from_attributes = True

class NotaCreditoUpdateSchema(BaseModel):
    documento_relacionado_id: Optional[int] = Field(None, ge=1, description="El ID del documento relacionado debe ser válido", example=1)
    operaciones: Optional[List[dict]] = Field(None, description="Debe especificar las operaciones de la nota de crédito", example=[{"operacion": "compra", "monto": 100.0}])
    montos_base_iva: Optional[List[dict]] = Field(None, description="Debe especificar los montos base para IVA", example=[{"base": 100.0, "iva": 16.0}])
    monto_exento: Optional[float] = Field(None, ge=0, description="El monto exento debe ser mayor o igual a 0", example=0.0)
    montos_iva: Optional[List[dict]] = Field(None, description="Debe especificar los montos de IVA", example=[{"base": 100.0, "iva": 16.0}])
    total: Optional[float] = Field(None, ge=0, description="El total debe ser mayor o igual a 0", example=116.0)

    class Config:
        from_attributes = True
