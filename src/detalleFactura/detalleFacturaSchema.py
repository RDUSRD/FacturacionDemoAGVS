from pydantic import BaseModel, Field
from typing import Optional


class DetalleFacturaSchema(BaseModel):
    factura_id: int = Field(
        ..., ge=1, description="El ID de la factura debe ser válido", example=1
    )
    producto_id: int = Field(
        ..., ge=1, description="El ID del producto debe ser válido", example=101
    )
    cantidad: int = Field(
        ..., ge=1, description="La cantidad debe ser mayor o igual a 1", example=2
    )

    class Config:
        from_attributes = True


class DetalleFacturaUpdateSchema(BaseModel):
    factura_id: Optional[int] = Field(
        None, ge=1, description="El ID de la factura debe ser válido", example=1
    )
    producto_id: Optional[int] = Field(
        None, ge=1, description="El ID del producto debe ser válido", example=101
    )
    cantidad: Optional[int] = Field(
        None, ge=1, description="La cantidad debe ser mayor o igual a 1", example=2
    )

    class Config:
        from_attributes = True
