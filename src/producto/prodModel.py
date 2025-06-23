from sqlalchemy import Column, Integer, String, Text, DECIMAL
from sqlalchemy.orm import relationship
from database import Base


class Producto(Base):
    __tablename__ = "producto"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="activo")
    stock = Column(Integer, nullable=False, default=0)

    detalles_factura = relationship("DetalleFactura", back_populates="producto")
