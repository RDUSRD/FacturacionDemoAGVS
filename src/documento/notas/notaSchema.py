from pydantic import Field
from typing import Optional
from src.documento.documentoSchema import DocumentoSchema, DocumentoUpdateSchema


class NotaCreditoSchema(DocumentoSchema):
    monto_credito: float = Field(
        ..., ge=0, description="Monto de la nota de crédito", example=500
    )
    descripcion: str = Field(
        ...,
        description="Descripción de la nota de crédito",
        example="Devolución de producto",
    )


class NotaCreditoUpdateSchema(DocumentoUpdateSchema):
    monto_credito: Optional[float] = Field(
        None, ge=0, description="Monto de la nota de crédito", example=500
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción de la nota de crédito",
        example="Devolución de producto",
    )


class NotaDebitoSchema(DocumentoSchema):
    monto_debito: float = Field(
        ..., ge=0, description="Monto de la nota de débito", example=300
    )
    descripcion: str = Field(
        ...,
        description="Descripción de la nota de débito",
        example="Ajuste por diferencia de precio",
    )


class NotaDebitoUpdateSchema(DocumentoUpdateSchema):
    monto_debito: Optional[float] = Field(
        None, ge=0, description="Monto de la nota de débito", example=300
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción de la nota de débito",
        example="Ajuste por diferencia de precio",
    )
