from datetime import datetime
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    rif = Column(String(50), unique=True, nullable=False)
    domicilio_fiscal = Column(Text, nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    date_created = Column(String(50), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date_updated = Column(String(50), nullable=True)

    documentos = relationship("Documento", back_populates="empresa")
