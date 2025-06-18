from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ComprobanteRetencion(Base):
    __tablename__ = "comprobante_retencion"
    id = Column(Integer, primary_key=True, index=True)
    documento_relacionado_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    tipo_impuesto = Column(String(50), nullable=False)
    monto_retenido = Column(DECIMAL(10, 2), nullable=False)

    documento_relacionado = relationship("Documento")
