from pydantic import BaseModel, Field
from typing import List, Optional

class OrdenEntregaSchema(BaseModel):
    bienes_entregados: List[str] = Field(..., description="Debe especificar los bienes entregados", example=["Producto A", "Producto B"])

    class Config:
        from_attributes = True

class OrdenEntregaUpdateSchema(BaseModel):
    bienes_entregados: Optional[List[str]] = Field(None, description="Debe especificar los bienes entregados", example=["Producto A", "Producto B"])

    class Config:
        from_attributes = True
