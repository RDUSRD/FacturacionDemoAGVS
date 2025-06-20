from pydantic import BaseModel, Field


class ClienteSchema(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="El nombre debe tener entre 3 y 255 caracteres",
        example="Cliente XYZ",
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

    class Config:
        from_attributes = True


class ClienteUpdateSchema(BaseModel):
    nombre: str = Field(
        None,
        min_length=3,
        max_length=255,
        description="El nombre debe tener entre 3 y 255 caracteres",
        example="Cliente XYZ",
    )
    rif: str = Field(
        None,
        pattern=r"^[JGVE]-\d{8}-\d$",
        description="El RIF debe tener el formato correcto",
        example="J-12345678-9",
    )
    domicilio_fiscal: str = Field(
        None,
        min_length=10,
        description="El domicilio fiscal debe ser válido",
        example="Av. Principal, Edificio XYZ, Caracas",
    )

    class Config:
        from_attributes = True
