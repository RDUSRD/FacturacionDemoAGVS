from pydantic import BaseModel, Field, model_validator


class ClienteSchema(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="El nombre debe tener entre 3 y 255 caracteres",
        example="Cliente XYZ",
    )
    documento: str = Field(
        ...,
        description="Número de documento del cliente",
        example="12345678",
    )
    tipo_documento: str = Field(
        ...,
        description="Tipo de documento, por ejemplo 'V', 'E', 'J', 'G'",
        example="V",
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="El teléfono debe ser válido",
        example="0412-3456789",
    )
    email: str = Field(
        ...,
        max_length=100,
        description="El correo electrónico debe ser válido",
        example="cliente@ejemplo.com",
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
                "documento": "12345678",
                "tipo_documento": "Cedula", # Cedula, Pasaporte, RIF
                "telefono": "0412-3456789",
                "email": "cliente@ejemplo.com",
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
    documento: str = Field(
        None,
        description="Número de documento del cliente",
        example="123456789",
    )
    tipo_documento: str = Field(
        None,
        description="Tipo de documento, por ejemplo 'V', 'E', 'J', 'G'",
        example="V",
    )
    telefono: str = Field(
        None,
        min_length=7,
        max_length=20,
        description="El teléfono debe ser válido",
        example="0412-3456789",
    )
    email: str = Field(
        None,
        max_length=100,
        description="El correo electrónico debe ser válido",
        example="cliente@ejemplo.com",
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
                "documento": "12345678",
                "tipo_documento": "V",
                "telefono": "0412-3456789",
                "email": "cliente@ejemplo.com",
                "domicilio_fiscal": "Av. Principal, Edificio XYZ, Caracas",
            }
        }
