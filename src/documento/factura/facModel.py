from sqlalchemy import Column, Integer, Float, ForeignKey
from src.documento.docModel import Documento
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean


class Factura(Documento):
    __tablename__ = "factura"
    factura_id = Column(Integer, primary_key=True)  # Eliminar autoincrement
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), nullable=False)  # Relación con Pedido
    descuento_total = Column(Float, nullable=True, default=0.0)
    total = Column(Float, nullable=True)
    aplica_igtf = Column(Boolean, nullable=False, default=False)  # Indica si aplica el IGTF
    monto_dolares = Column(Float, nullable=True, default=0.0)  # Monto en dólares si aplica

    detalles_factura = relationship(
        "DetalleFactura", back_populates="factura", cascade="all, delete-orphan"
    )
    pedido = relationship("Pedido", back_populates="facturas")  # Relación bidireccional

    __mapper_args__ = {
        "polymorphic_identity": "Factura",
    }
