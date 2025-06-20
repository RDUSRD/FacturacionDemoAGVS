from pydantic import BaseModel, Field
from typing import Optional

class ProductoSchema(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50, description="El código debe tener entre 3 y 50 caracteres", example="PROD123")
    descripcion: str = Field(..., min_length=10, description="La descripción debe ser válida", example="Producto de alta calidad")
    precio: float = Field(..., ge=0, description="El precio debe ser mayor o igual a 0", example=50.0)
    status: str = Field(..., description="El estado del producto", example="activo")

    class Config:
        from_attributes = True

class ProductoUpdateSchema(BaseModel):
    codigo: Optional[str] = Field(None, min_length=3, max_length=50, description="El código debe tener entre 3 y 50 caracteres", example="PROD123")
    descripcion: Optional[str] = Field(None, min_length=10, description="La descripción debe ser válida", example="Producto de alta calidad")
    precio: Optional[float] = Field(None, ge=0, description="El precio debe ser mayor o igual a 0", example=50.0)
    status: Optional[str] = Field(None, description="El estado del producto", example="activo")

    class Config:
        from_attributes = True
