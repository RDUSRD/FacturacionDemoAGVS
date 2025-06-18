from sqlalchemy import Column, Integer, JSON, ForeignKey
from src.documento.docModel import Documento

class OrdenEntrega(Documento):
    __tablename__ = "orden_entrega"

    id = Column(Integer, ForeignKey("documento.id"), primary_key=True)
    bienes_entregados = Column(JSON, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "orden_entrega"
    }
