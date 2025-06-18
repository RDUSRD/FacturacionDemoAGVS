from pydantic import BaseModel, Field

class ClienteSchema(BaseModel):
    id: int
    nombre: str = Field(..., min_length=3, max_length=255, description="El nombre debe tener entre 3 y 255 caracteres")
    rif: str = Field(..., regex=r"^[JGVE]-\d{8}-\d$", description="El RIF debe tener el formato correcto")
    domicilio_fiscal: str = Field(..., min_length=10, description="El domicilio fiscal debe ser válido")

    class Config:
        orm_mode = True
