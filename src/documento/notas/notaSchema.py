from pydantic import Field
from typing import Optional, List, Dict, Union
from src.documento.documentoSchema import DocumentoSchema


class NotaCreditoSchema(DocumentoSchema):
    monto_credito: Optional[float] = Field(
        None, ge=0, description="Monto de la nota de crédito"
    )

    factura_id: int = Field(
        None, ge=1, description="El ID de la factura debe ser válido", example=123
    )

    empresa_id: int = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=1
    )

    cliente_id: int = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=2
    )

    descripcion: str = Field(
        ...,
        description="Descripción de la nota de crédito"
    )
    modif_documento: Optional[Dict[str, Union[float, int]]] = Field(
        None,
        description="Modificaciones generales del documento (subtotal, IVA, total, etc.)"
    )
    modif_detalles: Optional[List[Dict[str, Union[int, float, bool]]]] = Field(
        None,
        description="Modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "factura_id": 123,
                "descripcion": "Devolución de producto por ajuste de precio",
                "modif_detalles": [
                    {
                        "id_producto": 1,
                        "cantidad": 2,
                        "precio_unitario": 75.0,
                        "descuento": 5.0,
                        "exento": False,
                        "total": 145.0
                    },
                    {
                        "id_producto": 2,
                        "cantidad": 1,
                        "precio_unitario": 50.0,
                        "descuento": 0.0,
                        "exento": True,
                        "total": 50.0
                    }
                ]
            }
        }



class NotaDebitoSchema(DocumentoSchema):
    monto_debito: Optional[float] = Field(
        None, ge=0, description="Monto de la nota de débito"
    )
    
    factura_id: int = Field(
        None, ge=1, description="El ID de la factura debe ser válido", example=123
    )
    
    empresa_id: int = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=1
    )

    cliente_id: int = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=2
    )
    
    descripcion: str = Field(
        ...,
        description="Descripción de la nota de débito"
    )
    modif_documento: Optional[Dict[str, Union[float, int]]] = Field(
        None,
        description="Modificaciones generales del documento (subtotal, IVA, total, etc.)"
    )
    modif_detalles: Optional[List[Dict[str, Union[int, float, bool]]]] = Field(
        None,
        description="Modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "factura_id": 123,
                "descripcion": "Ajuste por diferencia de precio",
                "modif_detalles": [
                    {
                        "id_producto": 1,
                        "cantidad": 3,
                        "precio_unitario": 100.0,
                        "descuento": 0.1,
                        "exento": False,
                        "total": 299.9
                    },
                    {
                        "id_producto": 3,
                        "cantidad": 1,
                        "precio_unitario": 75.0,
                        "descuento": 0.0,
                        "exento": True,
                        "total": 75.0
                    }
                ]
            }
        }