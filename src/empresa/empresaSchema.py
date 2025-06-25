from pydantic import BaseModel, Field
from typing import Optional


class EmpresaSchema(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="El nombre debe tener entre 3 y 255 caracteres",
        example="Empresa XYZ",
    )
    rif: str = Field(
        ...,
        pattern=r"^[JGVE]-\d{8}-\d$",
        description="El RIF debe tener el formato correcto",
        example="J-12345678-9",
    )
    domicilio_fiscal: str = Field(
        ...,
        min_length=10,
        description="El domicilio fiscal debe ser válido",
        example="Av. Principal, Edificio XYZ, Caracas",
    )
    telefono: str = Field(
        ...,
        pattern=r"^\+?\d{10,15}$",
        description="El teléfono debe ser válido",
        example="+584121234567",
    )
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="El correo electrónico debe ser válido",
        example="contacto@empresa.com",
    )

    class Config:
        from_attributes = True


class EmpresaUpdateSchema(BaseModel):
    nombre: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="El nombre debe tener entre 3 y 255 caracteres",
        example="Empresa XYZ",
    )
    rif: Optional[str] = Field(
        None,
        pattern=r"^[JGVE]-\d{8}-\d$",
        description="El RIF debe tener el formato correcto",
        example="J-12345678-9",
    )
    domicilio_fiscal: Optional[str] = Field(
        None,
        min_length=10,
        description="El domicilio fiscal debe ser válido",
        example="Av. Principal, Edificio XYZ, Caracas",
    )
    telefono: Optional[str] = Field(
        None,
        pattern=r"^\+?\d{10,15}$",
        description="El teléfono debe ser válido",
        example="+584121234567",
    )
    email: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="El correo electrónico debe ser válido",
        example="contacto@empresa.com",
    )

    date_updated: Optional[str] = Field(
        None,
        description="Fecha de actualización de la empresa en formato ISO 8601",
        example="2023-10-02T12:00:00Z",
    )

    class Config:
        from_attributes = True
