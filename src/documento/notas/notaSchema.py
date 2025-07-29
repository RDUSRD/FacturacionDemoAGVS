from pydantic import Field
from typing import Optional, List, Dict, Union
from src.documento.documentoSchema import DocumentoSchema


class NotaCreditoSchema(DocumentoSchema):
    monto_credito: float = Field(
        ..., ge=0, description="Monto de la nota de crédito", example=500
    )
    descripcion: str = Field(
        ...,
        description="Descripción de la nota de crédito",
        example="Devolución de producto",
    )
    modif_documento: Optional[Dict[str, Union[float, int]]] = Field(
        None,
        description="Modificaciones generales del documento (subtotal, IVA, total, etc.)",
        example={"subtotal": 150.0, "iva": 18.0, "total": 168.0},
    )
    modif_detalles: Optional[List[Dict[str, Union[int, float]]]] = Field(
        None,
        description="Modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)",
        example=[
            {
                "id_producto": 1,
                "cantidad": 2,
                "precio_unitario": 100.0,
                "descuento": 0.1,
            },
            {
                "id_producto": 2,
                "cantidad": 0,  # Producto eliminado
                "precio_unitario": 50.0,
                "descuento": 0.05,
            },
        ],
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
    modif_documento: Optional[Dict[str, Union[float, int]]] = Field(
        None,
        description="Modificaciones generales del documento (subtotal, IVA, total, etc.)",
        example={"subtotal": 250.0, "iva": 30.0, "total": 280.0},
    )
    modif_detalles: Optional[List[Dict[str, Union[int, float]]]] = Field(
        None,
        description="Modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)",
        example=[
            {
                "id_producto": 1,
                "cantidad": 3,
                "precio_unitario": 100.0,
                "descuento": 0.1,
            },
            {
                "id_producto": 3,
                "cantidad": 1,  # Producto agregado
                "precio_unitario": 75.0,
                "descuento": 0.0,
            },
        ],
    )