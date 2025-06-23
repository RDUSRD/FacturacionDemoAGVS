from pydantic import Field
from src.documento.documentoSchema import DocumentoSchema


class OrdenEntregaSchema(DocumentoSchema):
    detalles_entrega: dict = Field(
        ...,
        description="Detalles de la orden de entrega",
        example={"producto": "Laptop", "cantidad": 2},
    )
