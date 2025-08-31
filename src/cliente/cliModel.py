from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "cliente"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    documento = Column(String(50), unique=True, nullable=False)
    tipo_documento = Column(String(50), nullable=False)
    domicilio_fiscal = Column(Text, nullable=False)
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    date_created = Column(String(50), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date_updated = Column(String(50), nullable=True)

    documentos = relationship("Documento", back_populates="cliente")
    pedidos = relationship("Pedido", back_populates="cliente")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
