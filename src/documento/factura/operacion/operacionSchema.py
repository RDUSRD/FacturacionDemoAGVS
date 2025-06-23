from pydantic import BaseModel, Field

class OperacionSchema(BaseModel):
    tipo: str = Field(..., description="Tipo de operación", example="venta")
    monto: float = Field(..., ge=0, description="Monto de la operación", example=1000)

    class Config:
        from_attributes = True
