from pydantic import BaseModel, Field
from typing import Optional


class PedidoSchema(BaseModel):
    cliente_id: int = Field(
        ..., ge=1, description="El ID del cliente debe ser válido", example=1
    )
    empresa_id: int = Field(
        ..., ge=1, description="El ID de la empresa debe ser válido", example=101
    )
    estado: Optional[str] = Field(
        "Pendiente", description="Estado del pedido", example="Pendiente"
    )
    total: Optional[float] = Field(
        None, ge=0, description="El total debe ser mayor o igual a 0", example=500.00
    )
    tasa_cambio: Optional[float] = Field(
        None,
        ge=0,
        description="La tasa de cambio debe ser mayor o igual a 0",
        example=1.00,
    )
    observaciones: Optional[str] = Field(
        None, description="Observaciones del pedido", example="Pedido urgente"
    )
    detalles_pedido: Optional[list] = Field(
        None,
        description="Detalles del pedido",
        example=[
            {"producto_id": 1, "cantidad": 2, "precio": 250.00},
            {"producto_id": 2, "cantidad": 1, "precio": 250.00},
        ],
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "cliente_id": 1,
                "empresa_id": 1,
                "observaciones": "Pedido urgente",
                "detalles_pedido": [
                    {"producto_id": 1, "cantidad": 2},
                    {"producto_id": 2, "cantidad": 1},
                ],
            }
        }


class PedidoUpdateSchema(BaseModel):
    cliente_id: Optional[int] = Field(
        None, ge=1, description="El ID del cliente debe ser válido", example=1
    )
    empresa_id: Optional[int] = Field(
        None, ge=1, description="El ID de la empresa debe ser válido", example=101
    )
    estado: Optional[str] = Field(
        None, description="Estado del pedido", example="Pendiente"
    )
    total: Optional[float] = Field(
        None, ge=0, description="El total debe ser mayor o igual a 0", example=500.00
    )
    tasa_cambio: Optional[float] = Field(
        None,
        ge=0,
        description="La tasa de cambio debe ser mayor o igual a 0",
        example=1.00,
    )
    observaciones: Optional[str] = Field(
        None, description="Observaciones del pedido", example="Pedido urgente"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "cliente_id": 1,
                "empresa_id": 101,
                "observaciones": "Pedido urgente",
                "detalles_pedido": [
                    {"producto_id": 1, "cantidad": 2},
                    {"producto_id": 2, "cantidad": 1},
                ],
            }
        }
