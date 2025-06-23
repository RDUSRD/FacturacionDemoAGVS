from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


class Operacion(Base):
    __tablename__ = "operacion"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(
        Integer, ForeignKey("factura.id", ondelete="SET NULL"), nullable=True
    )
    tipo = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
