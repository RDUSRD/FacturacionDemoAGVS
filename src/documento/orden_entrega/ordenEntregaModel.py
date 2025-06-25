from sqlalchemy import Column, Integer, JSON, ForeignKey
from src.documento.docModel import Documento


class OrdenEntrega(Documento):
    __tablename__ = "orden_entrega"

    orden_entrega_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    bienes_entregados = Column(JSON, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "Orden_entrega"}
