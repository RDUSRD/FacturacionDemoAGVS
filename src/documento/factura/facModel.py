from sqlalchemy import Column, Integer, Float, ForeignKey
from src.documento.docModel import Documento
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean


class Factura(Documento):
    __tablename__ = "factura"
    factura_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    descuento_total = Column(Float, nullable=True, default=0.0)
    total = Column(Float, nullable=True)
    aplica_igtf = Column(Boolean, nullable=False, default=False)  # Indica si aplica el IGTF
    monto_igtf = Column(Float, nullable=True, default=0.0)  # Monto del IGTF si aplica

    detalles_factura = relationship(
        "DetalleFactura", back_populates="factura", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "Factura",
    }
