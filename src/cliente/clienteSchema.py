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
        json_schema_extra = {
            "example": {
                "nombre": "Cliente XYZ",
                "rif": "J-12345678-9",
                "domicilio_fiscal": "Av. Principal, Edificio XYZ, Caracas",
            }
        }


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

    date_updated: str = Field(
        None,
        description="Fecha de actualización del cliente en formato ISO 8601",
        example="2023-10-02T12:00:00Z",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nombre": "Cliente XYZ",
                "rif": "J-12345678-9",
                "domicilio_fiscal": "Av. Principal, Edificio XYZ, Caracas",
            }
        }
