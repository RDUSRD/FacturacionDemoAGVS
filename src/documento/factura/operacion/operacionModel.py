from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Operacion(Base):
    __tablename__ = "operacion"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    tipo = Column(String, nullable=False)
    monto = Column(Float, nullable=False)

    factura = relationship("Factura", back_populates="operaciones")