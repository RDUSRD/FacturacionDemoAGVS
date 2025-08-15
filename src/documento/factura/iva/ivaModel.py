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
    monto_base_general = Column(Float, nullable=True)  # Base para alícuota general (16%)
    monto_base_reducida = Column(Float, nullable=True)  # Base para alícuota reducida (8%)
    monto_base_adicional = Column(Float, nullable=True)  # Base para alícuota adicional (15%)
    iva_general = Column(Float, nullable=True)  # IVA calculado para alícuota general
    iva_reducida = Column(Float, nullable=True)  # IVA calculado para alícuota reducida
    iva_adicional = Column(Float, nullable=True)  # IVA calculado para alícuota adicional
