from pydantic import BaseModel, Field

class DetalleFacturaSchema(BaseModel):
    id: int
    factura_id: int = Field(..., ge=1, description="El ID de la factura debe ser válido")
    producto_id: int = Field(..., ge=1, description="El ID del producto debe ser válido")
    descripcion: str = Field(..., min_length=10, description="La descripción debe ser válida")
    precio: float = Field(..., ge=0, description="El precio debe ser mayor o igual a 0")
    cantidad: int = Field(..., ge=1, description="La cantidad debe ser mayor o igual a 1")
    total: float = Field(..., ge=0, description="El total debe ser mayor o igual a 0")

    class Config:
        orm_mode = True
