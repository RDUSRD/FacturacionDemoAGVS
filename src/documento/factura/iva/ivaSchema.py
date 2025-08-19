from pydantic import BaseModel, Field


class IVASchema(BaseModel):
    base: float = Field(
        ..., ge=0, description="Base imponible para el cálculo de IVA", example=800
    )

    subtotal_descuento: float = Field(
        ..., ge=0, description="Subtotal con descuento aplicado", example=800
    )
    subtotal_sin_descuento: float = Field(
        ..., ge=0, description="Subtotal sin descuento aplicado", example=800
    )

    monto_exento: float = Field(
        ..., ge=0, description="Monto exento de IVA", example=200
    )

    monto: float = Field(
        ..., ge=0, description="Monto total calculado incluyendo IVA", example=960
    )

    monto_base_general: float = Field(
        0, ge=0, description="Base imponible para alícuota general (16%)", example=500
    )
    monto_base_reducida: float = Field(
        0, ge=0, description="Base imponible para alícuota reducida (8%)", example=300
    )
    monto_base_adicional: float = Field(
        0, ge=0, description="Base imponible para alícuota adicional (15%)", example=100
    )

    iva_general: float = Field(
        16,
        ge=0,
        description="Porcentaje de IVA aplicado para alícuota general (16%)",
        example=16,
    )
    iva_general_monto: float = Field(
        ...,
        ge=0,
        description="Monto de IVA aplicado para alícuota general (16%)",
        example=80,
    )
    iva_reducida: float = Field(
        8,
        ge=0,
        description="Porcentaje de IVA aplicado para alícuota reducida (8%)",
        example=8,
    )
    iva_reducida_monto: float = Field(
        ...,
        ge=0,
        description="Monto de IVA aplicado para alícuota reducida (8%)",
        example=24,
    )
    iva_adicional: float = Field(
        15,
        ge=0,
        description="Porcentaje de IVA aplicado para alícuota adicional (15%)",
        example=15,
    )
    iva_adicional_monto: float = Field(
        ...,
        ge=0,
        description="Monto de IVA aplicado para alícuota adicional (15%)",
        example=15,
    )

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
