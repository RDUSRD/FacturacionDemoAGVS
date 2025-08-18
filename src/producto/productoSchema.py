from pydantic import BaseModel, Field, field_validator
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
    alicuota_iva: float = Field(
        ...,
        description="Porcentaje de IVA aplicado al producto (solo 8.0, 16.0 o 15.0, dependiendo de la clasificación del producto)",
        example=16.0,
    )
    exento: bool = Field(
        False,
        description="Indica si el producto está exento de impuestos",
        example=False,
    )
    descuento: Optional[float] = Field(
        0.0,
        ge=0,
        le=1,
        description="Porcentaje de descuento aplicado al producto (entre 0 y 1)",
        example=0.1,
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "descripcion": "Producto de alta calidad",
                "precio": 50.0,
                "status": "activo",
                "stock": 100,
                "alicuota_iva": 16.0,
                "exento": False,
                "descuento": 0.1,  # Representa un 10% de descuento
            }
        }

    @field_validator("alicuota_iva")
    def validate_alicuota_iva(cls, value):
        if value not in {8.0, 16.0, 15.0}:
            raise ValueError("La alícuota de IVA debe ser 8.0, 16.0 o 15.0.")
        return value


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
    alicuota_iva: Optional[float] = Field(
        None,
        description="Porcentaje de IVA aplicado al producto (solo 8.0, 16.0 o 15.0, dependiendo de la clasificación del producto)",
        example=16.0,
    )
    exento: Optional[bool] = Field(
        None,
        description="Indica si el producto está exento de impuestos",
        example=False,
    )
    descuento: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Porcentaje de descuento aplicado al producto (entre 0 y 1)",
        example=10.0,
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "descripcion": "Producto de alta calidad",
                "precio": 50.0,
                "status": "activo",
                "stock": 100,
                "alicuota_iva": 16.0,
                "exento": False,
                "descuento": 0.1,  # Representa un 10% de descuento
            }
        }

    @field_validator("alicuota_iva")
    def validate_alicuota_iva(cls, value):
        if value not in {8.0, 16.0, 15.0}:
            raise ValueError("La alícuota de IVA debe ser 8.0, 16.0 o 15.0.")
        return value
