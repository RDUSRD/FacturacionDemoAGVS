from sqlalchemy import Column, Integer, Numeric, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from database import Base

class Documento(Base):
    __tablename__ = "documento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)  # Desactivar autoincremento
    tipo_documento = Column(String(50), nullable=False)
    numero_control = Column(String(50), nullable=True)
    fecha_emision = Column(Date, nullable=False)
    hora_emision = Column(Time, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    estado = Column(String(50), nullable=False)
    tasa_cambio = Column(Numeric(10, 4), nullable=True)
    fecha_numero_control = Column(Date, nullable=True)
    hora_numero_control = Column(Time, nullable=True)

    empresa = relationship("Empresa", back_populates="documentos")
    cliente = relationship("Cliente", back_populates="documentos")

    @declared_attr
    def __mapper_args__(cls):
        return {
            "polymorphic_on": cls.tipo_documento,
            "polymorphic_identity": "documento"
        }
