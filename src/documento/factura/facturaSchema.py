from pydantic import Field
from src.documento.documentoSchema import DocumentoSchema


class FacturaSchema(DocumentoSchema):
    monto_exento: float = Field(
        ..., ge=0, description="Monto exento de impuestos", example=200
    )
    total: float = Field(
        ..., ge=0, description="Monto total de la factura", example=1160
    )
    operaciones: list = Field(
        ...,
        description="Lista de operaciones asociadas a la factura",
        example=[{"tipo": "venta", "monto": 1000}],
    )
    impuestos: list = Field(
        ...,
        description="Lista de impuestos aplicados a la factura",
        example=[{"base": 800, "monto": 160}],
    )
    detalles_factura: list = Field(
        ...,
        description="Lista de detalles de la factura",
        example=[{"factura_id": 1, "producto_id": 1, "cantidad": 2}],
    )
