from sqlalchemy import Column, Integer, Text, DECIMAL, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class DetalleFactura(Base):
    __tablename__ = "detalle_factura"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    descripcion = Column(Text, nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    cantidad = Column(Integer, nullable=False)  # Cambiado a Integer para representar cantidades enteras
    total = Column(DECIMAL(10, 2), nullable=False)

    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_factura")
    

    __table_args__ = (
        CheckConstraint("precio >= 0", name="check_precio_positive"),
        CheckConstraint("cantidad >= 0", name="check_cantidad_positive"),
        CheckConstraint("total >= 0", name="check_total_positive"),
    )
