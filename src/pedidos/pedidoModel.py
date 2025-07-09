from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=False)
    estado = Column(String(50), default="Pendiente")
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    total = Column(Numeric(10, 2), nullable=True)
    observaciones = Column(String(255), nullable=True)

    cliente = relationship("Cliente", back_populates="pedidos")
    empresa = relationship("Empresa", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
