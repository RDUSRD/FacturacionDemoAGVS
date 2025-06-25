from sqlalchemy import Column, Integer, Float, ForeignKey
from database import Base


class iva(Base):
    __tablename__ = "iva"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(
        Integer, ForeignKey("factura.factura_id", ondelete="SET NULL"), nullable=True
    )
    base = Column(Float, nullable=False)
    monto_exento = Column(Float, nullable=False)
    monto = Column(Float, nullable=False)
