from sqlalchemy import Column, Integer, Float, ForeignKey
from src.documento.docModel import Documento
from sqlalchemy.orm import relationship


class Factura(Documento):
    __tablename__ = "factura"
    id = Column(Integer, ForeignKey("documento.id"), primary_key=True)
    monto_exento = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    detalles_factura = relationship(
        "DetalleFactura", back_populates="factura", cascade="all, delete-orphan"
    )

    __mapper_args__ = {"polymorphic_identity": "Factura"}
