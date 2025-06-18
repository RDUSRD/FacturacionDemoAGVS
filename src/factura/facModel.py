from sqlalchemy import Column, Integer, Float, JSON, ForeignKey
from src.documento.docModel import Documento

class Factura(Documento):
    __tablename__ = "factura"

    id = Column(Integer, ForeignKey("documento.id"), primary_key=True)
    operaciones = Column(JSON, nullable=False)
    montos_base_iva = Column(JSON, nullable=False)
    monto_exento = Column(Float, nullable=False)
    montos_iva = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "factura"
    }
