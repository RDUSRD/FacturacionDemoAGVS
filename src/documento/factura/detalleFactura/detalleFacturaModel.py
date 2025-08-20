from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class DetalleFactura(Base):
    __tablename__ = "detalle_factura"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("factura.factura_id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)  # Cambiado a Integer para representar cantidades enteras
    descuento = Column(DECIMAL(10, 2), nullable=True, default=0.0)  # Descuento aplicado al detalle
    alicuota_iva = Column(DECIMAL(5, 2), nullable=True, default=0.0)  # Porcentaje de alícuota del IVA
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)

    producto = relationship("Producto", back_populates="detalles_factura")
    factura = relationship("Factura", back_populates="detalles_factura")

    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="check_cantidad_positive"),
        CheckConstraint("total >= 0", name="check_total_positive"),
    )
