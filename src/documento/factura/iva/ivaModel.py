from sqlalchemy import Column, Integer, Float, ForeignKey
from database import Base


class iva(Base):
    __tablename__ = "iva"
    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(
        Integer, ForeignKey("factura.factura_id", ondelete="SET NULL"), nullable=True
    )
    subtotal_sin_descuento = Column(Float, nullable=False)
    subtotal_descuento = Column(Float, nullable=False)
    base = Column(Float, nullable=False)  # suma de todas las bases
    monto_exento = Column(Float, nullable=False)
    monto = Column(Float, nullable=False)
    monto_base_general = Column(
        Float, nullable=True
    )  # Base para alícuota general (16%)
    monto_base_reducida = Column(
        Float, nullable=True
    )  # Base para alícuota reducida (8%)
    monto_base_adicional = Column(
        Float, nullable=True
    )  # Base para alícuota adicional (15%)
    iva_general = Column(Float, nullable=True)  # IVA calculado para alícuota general
    iva_general_monto = Column(Float, nullable=True)  # Monto del IVA general
    iva_reducida = Column(Float, nullable=True)  # IVA calculado para alícuota reducida
    iva_reducida_monto = Column(Float, nullable=True)  # Monto del IVA reducido
    iva_adicional = Column(
        Float, nullable=True
    )  # IVA calculado para alícuota adicional (15%)
    iva_adicional_monto = Column(Float, nullable=True)  # Monto del IVA adicional
    igtf = Column(Float, nullable=True)  # IVA General de Transacciones Financieras
    base_igtf = Column(Float, nullable=True)  # Base para cálculo del IGTF
    monto_igtf = Column(Float, nullable=True)  # Monto del IGTF