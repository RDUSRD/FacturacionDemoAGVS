from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.documento.docModel import Documento
from database import Base


class Factura(Documento):
    __tablename__ = "factura"
    id = Column(Integer, ForeignKey("documento.id"), primary_key=True)
    monto_exento = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    operaciones = relationship("Operacion", back_populates="factura")
    impuestos = relationship("iva", back_populates="factura")
    detalles = relationship("DetalleFactura", back_populates="factura")

    __mapper_args__ = {"polymorphic_identity": "Factura"}
