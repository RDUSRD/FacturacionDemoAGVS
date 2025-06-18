from pydantic import BaseModel, Field

class ProductoSchema(BaseModel):
    id: int
    codigo: str = Field(..., min_length=3, max_length=50, description="El código debe tener entre 3 y 50 caracteres")
    descripcion: str = Field(..., min_length=10, description="La descripción debe ser válida")
    precio: float = Field(..., ge=0, description="El precio debe ser mayor o igual a 0")

    class Config:
        orm_mode = True
