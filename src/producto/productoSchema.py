from pydantic import BaseModel, Field
from typing import Optional


class ProductoSchema(BaseModel):
    codigo: str = Field(
        None,
        min_length=3,
        max_length=50,
        description="El código debe tener entre 3 y 50 caracteres",
        example="PROD123",
    )
    descripcion: str = Field(
        ...,
        min_length=10,
        description="La descripción debe ser válida",
        example="Producto de alta calidad",
    )
    precio: float = Field(
        ..., ge=0, description="El precio debe ser mayor o igual a 0", example=50.0
    )
    status: str = Field(..., description="El estado del producto", example="activo")
    stock: int = Field(
        ..., ge=0, description="El stock debe ser mayor o igual a 0", example=100
    )
    codigo_barras: Optional[str] = Field(
        None,
        max_length=100,
        description="El código de barras debe ser único",
        example="1234567890123",
    )
    codigo_QR: Optional[str] = Field(
        None,
        max_length=100,
        description="El código QR debe ser único",
        example="QR123456789",
    )
    exento: bool = Field(
        False,
        description="Indica si el producto está exento de impuestos",
        example=False,
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "descripcion": "Producto de alta calidad",
                "precio": 50.0,
                "status": "activo",
                "stock": 100,
                "exento": False,
            }
        }


class ProductoUpdateSchema(BaseModel):
    codigo: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="El código debe tener entre 3 y 50 caracteres",
        example="PROD123",
    )
    descripcion: Optional[str] = Field(
        None,
        min_length=10,
        description="La descripción debe ser válida",
        example="Producto de alta calidad",
    )
    precio: Optional[float] = Field(
        None, ge=0, description="El precio debe ser mayor o igual a 0", example=50.0
    )
    status: Optional[str] = Field(
        None, description="El estado del producto", example="activo"
    )
    stock: Optional[int] = Field(
        None, ge=0, description="El stock debe ser mayor o igual a 0", example=100
    )
    codigo_barras: Optional[str] = Field(
        None,
        max_length=100,
        description="El código de barras debe ser único",
        example="1234567890123",
    )
    codigo_QR: Optional[str] = Field(
        None,
        max_length=100,
        description="El código QR debe ser único",
        example="QR123456789",
    )
    exento: Optional[bool] = Field(
        None,
        description="Indica si el producto está exento de impuestos",
        example=False,
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "descripcion": "Producto de alta calidad",
                "precio": 50.0,
                "status": "activo",
                "stock": 100,
                "exento": False,
            }
        }
