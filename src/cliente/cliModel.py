from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Cliente(Base):
    __tablename__ = "cliente"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    rif = Column(String(50), unique=True, nullable=False)
    domicilio_fiscal = Column(Text, nullable=False)

    documentos = relationship("Documento", back_populates="cliente")
