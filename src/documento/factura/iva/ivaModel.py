from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class iva(Base):
    __tablename__ = "iva"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("factura.id"), nullable=False)
    base = Column(Float, nullable=False)
    monto = Column(Float, nullable=False)

    factura = relationship("Factura", back_populates="impuestos")
