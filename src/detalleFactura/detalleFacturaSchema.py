from pydantic import BaseModel, Field
from typing import Optional

class DetalleFacturaSchema(BaseModel):
    factura_id: int = Field(..., ge=1, description="El ID de la factura debe ser válido", example=1)
    producto_id: int = Field(..., ge=1, description="El ID del producto debe ser válido", example=101)
    descripcion: str = Field(..., min_length=10, description="La descripción debe ser válida", example="Producto de alta calidad")
    precio: float = Field(..., ge=0, description="El precio debe ser mayor o igual a 0", example=50.0)
    cantidad: int = Field(..., ge=1, description="La cantidad debe ser mayor o igual a 1", example=2)
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0", example=100.0)

    class Config:
        from_attributes = True

class DetalleFacturaUpdateSchema(BaseModel):
    factura_id: Optional[int] = Field(None, ge=1, description="El ID de la factura debe ser válido", example=1)
    producto_id: Optional[int] = Field(None, ge=1, description="El ID del producto debe ser válido", example=101)
    descripcion: Optional[str] = Field(None, min_length=10, description="La descripción debe ser válida", example="Producto de alta calidad")
    precio: Optional[float] = Field(None, ge=0, description="El precio debe ser mayor o igual a 0", example=50.0)
    cantidad: Optional[int] = Field(None, ge=1, description="La cantidad debe ser mayor o igual a 1", example=2)
    total: Optional[float] = Field(None, ge=0, description="El total debe ser mayor o igual a 0", example=100.0)

    class Config:
        from_attributes = True
