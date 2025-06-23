from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional


class DocumentoSchema(BaseModel):
    tipo_documento: str = Field(
        ..., description="Debe especificar el tipo de documento", example="Factura"
    )
    numero_control: str = Field(
        ...,
        pattern=r"^\d{8}$",
        description="El número de control debe tener 8 dígitos",
        example="12345678",
    )
    fecha_emision: Optional[date] = Field(
        None, description="La fecha de emisión debe ser válida", example="2025-06-20"
    )
    hora_emision: Optional[time] = Field(
        None, description="La hora de emisión debe ser válida", example="14:30:00"
    )
    empresa_id: int = Field(
        ..., ge=1, description="El ID de la empresa debe ser válido", example=1
    )
    cliente_id: int = Field(
        ..., ge=1, description="El ID del cliente debe ser válido", example=2
    )
    estado: str = Field(
        ..., description="Debe especificar el estado del documento", example="Activo"
    )

    class Config:
        from_attributes = True


class DocumentoUpdateSchema(BaseModel):
    tipo_documento: Optional[str] = Field(
        None, description="Debe especificar el tipo de documento", example="Factura"
    )
    numero_control: Optional[str] = Field(
        None,
        pattern=r"^\d{8}$",
        description="El número de control debe tener 8 dígitos",
        example="12345678",
    )
    fecha_emision: Optional[date] = Field(
        None, description="La fecha de emisión debe ser válida", example="2025-06-20"
    )
    hora_emision: Optional[time] = Field(
        None, description="La hora de emisión debe ser válida", example="14:30:00"
    )
    empresa_id: Optional[int] = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=1
    )
    cliente_id: Optional[int] = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=2
    )
    estado: Optional[str] = Field(
        None, description="Debe especificar el estado del documento", example="Activo"
    )

    class Config:
        from_attributes = True


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


class OperacionSchema(BaseModel):
    tipo: str = Field(..., description="Tipo de operación", example="venta")
    monto: float = Field(..., ge=0, description="Monto de la operación", example=1000)


class IVASchema(BaseModel):
    base: float = Field(
        ..., ge=0, description="Base imponible para el cálculo de IVA", example=800
    )
    monto: float = Field(..., ge=0, description="Monto de IVA calculado", example=160)


class DetalleFacturaSchema(BaseModel):
    factura_id: int = Field(
        ..., ge=1, description="ID de la factura asociada al detalle", example=1
    )
    producto_id: int = Field(
        ..., ge=1, description="ID del producto asociado al detalle", example=1
    )
    cantidad: int = Field(
        ..., ge=0, description="Cantidad del producto en el detalle", example=2
    )


# Editar luego:
class OrdenEntregaSchema(DocumentoSchema):
    detalles_entrega: dict = Field(
        ...,
        description="Detalles de la orden de entrega",
        example={"producto": "Laptop", "cantidad": 2},
    )


class NotaCreditoSchema(DocumentoSchema):
    monto_credito: float = Field(
        ..., ge=0, description="Monto de la nota de crédito", example=500
    )


class NotaDebitoSchema(DocumentoSchema):
    monto_debito: float = Field(
        ..., ge=0, description="Monto de la nota de débito", example=300
    )
