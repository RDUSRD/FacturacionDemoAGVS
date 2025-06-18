from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from database import Base

class Documento(Base):
    __tablename__ = "documento"

    id = Column(Integer, primary_key=True, index=True)
    tipo_documento = Column(String(50), nullable=False)
    numero_control = Column(String(50), nullable=False)
    fecha_emision = Column(Date, nullable=False)
    hora_emision = Column(Time, nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    estado = Column(String(50), nullable=False)

    empresa = relationship("Empresa", back_populates="documentos")
    cliente = relationship("Cliente", back_populates="documentos")

    @declared_attr
    def __mapper_args__(cls):
        return {
            "polymorphic_on": cls.tipo_documento,
            "polymorphic_identity": "documento"
        }
