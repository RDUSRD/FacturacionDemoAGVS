from pydantic import BaseModel, Field
from typing import List

class OrdenEntregaSchema(BaseModel):
    id: int
    bienes_entregados: List[str] = Field(..., description="Debe especificar los bienes entregados")

    class Config:
        orm_mode = True
