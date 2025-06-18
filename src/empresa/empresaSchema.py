from pydantic import BaseModel, Field

class EmpresaSchema(BaseModel):
    id: int
    nombre: str = Field(..., min_length=3, max_length=255, description="El nombre debe tener entre 3 y 255 caracteres")
    rif: str = Field(..., regex=r"^[JGVE]-\d{8}-\d$", description="El RIF debe tener el formato correcto")
    domicilio_fiscal: str = Field(..., min_length=10, description="El domicilio fiscal debe ser válido")
    telefono: str = Field(..., regex=r"^\+?\d{10,15}$", description="El teléfono debe ser válido")
    email: str = Field(..., regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="El correo electrónico debe ser válido")

    class Config:
        orm_mode = True
