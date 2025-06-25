from pydantic import BaseModel, Field


class IVASchema(BaseModel):
    base: float = Field(
        ..., ge=0, description="Base imponible para el cálculo de IVA", example=800
    )

    monto_exento: float = Field(
        ..., ge=0, description="Monto exento de IVA", example=200
    )

    monto: float = Field(..., ge=0, description="Monto de IVA calculado", example=160)

    factura_id: int = Field(
        ..., ge=1, description="ID de la factura asociada al detalle", example=1
    )
    producto_id: int = Field(
        ..., ge=1, description="ID del producto asociado al detalle", example=1
    )
    cantidad: int = Field(
        ..., ge=0, description="Cantidad del producto en el detalle", example=2
    )

    class Config:
        from_attributes = True
