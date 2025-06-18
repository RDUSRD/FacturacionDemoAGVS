from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    rif = Column(String(50), unique=True, nullable=False)
    domicilio_fiscal = Column(Text, nullable=False)
    telefono = Column(String(20), nullable=False)  # Ajustado a obligatorio según el diagrama
    email = Column(String(255), nullable=False)    # Ajustado a obligatorio según el diagrama

    documentos = relationship("Documento", back_populates="empresa")
