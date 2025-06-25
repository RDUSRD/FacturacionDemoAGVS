from sqlalchemy import Column, Integer, Float, ForeignKey
from src.documento.docModel import Documento
from sqlalchemy.orm import relationship


class Factura(Documento):
    __tablename__ = "factura"
    factura_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    total = Column(Float, nullable=True)

    detalles_factura = relationship(
        "DetalleFactura", back_populates="factura", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "Factura",
    }
