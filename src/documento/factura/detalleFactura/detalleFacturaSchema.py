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
    alicuota_iva: float = Field(
        ...,
        ge=0,
        description="La alícuota del IVA debe ser mayor o igual a 0",
        example=16.00,
    )
    precio_unitario: float = Field(
        ...,
        ge=0,
        description="El precio unitario debe ser mayor o igual a 0",
        example=100.00,
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
    alicuota_iva: Optional[float] = Field(
        None,
        ge=0,
        description="La alícuota del IVA debe ser mayor o igual a 0",
        example=16.00,
    )
    precio_unitario: Optional[float] = Field(
        None,
        ge=0,
        description="El precio unitario debe ser mayor o igual a 0",
        example=100.00,
    )

    class Config:
        from_attributes = True
