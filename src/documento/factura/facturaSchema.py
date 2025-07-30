from pydantic import Field
from src.documento.documentoSchema import DocumentoSchema
from typing import Optional


class FacturaSchema(DocumentoSchema):
    tipo_documento: str = Field(
        None, description="Debe especificar el tipo de documento", example="Factura"
    )
    cliente_id: int = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=2
    )
    empresa_id: int = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=1
    )
    descuento_total: Optional[float] = Field(
        None, ge=0, description="Monto del descuento aplicado a la factura", example=100
    )
    total: Optional[float] = Field(
        None, ge=0, description="Monto total de la factura", example=1160
    )
    impuestos: Optional[list] = Field(
        None,
        description="Lista de impuestos aplicados a la factura",
        example=[{"base": 800, "monto": 160}],
    )
    operaciones: Optional[list] = Field(
        None,
        description="Lista de operaciones asociadas a la factura",
        example=[{"tipo": "venta", "monto": 1000}],
    )
    detalles_factura: list = Field(
        None,
        description="Lista de detalles de la factura",
        example=[{"producto_id": 1, "cantidad": 2}],
    )
    aplica_igtf: bool = Field(..., description="Indica si aplica el IGTF", example=True)
    monto_igtf: Optional[float] = Field(
        None, ge=0, description="Monto del IGTF si aplica", example=20.0
    )
    pedido_id: int = Field(
        ..., ge=1, description="El ID del pedido asociado a la factura", example=1
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "aplica_igtf": True,
                "pedido_id": 1,
            }
        }
