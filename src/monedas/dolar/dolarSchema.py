from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class DolarBase(BaseModel):
    fecha: date = Field(
        ..., description="Fecha del precio del dólar"
    )
    precio: float = Field(
        ..., ge=0, description="Precio del dólar en dos decimales"
    )
    fecha_actualizacion: datetime = Field(
        ..., description="Fecha y hora de la última actualización"
    )


class DolarCreateSchema(DolarBase):
    pass


class DolarUpdateSchema(BaseModel):
    fecha: Optional[date] = Field(
        None, description="Fecha del precio del dólar"
    )
    precio: Optional[float] = Field(
        None, ge=0, description="Precio del dólar en dos decimales"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None, description="Fecha y hora de la última actualización"
    )

    class Config:
        from_attributes = True
