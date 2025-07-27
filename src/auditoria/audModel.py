from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    tabla_afectada = Column(String(255), nullable=False)
    registro_id = Column(Integer, nullable=False)
    accion = Column(String(50), nullable=False)
    detalles = Column(Text, nullable=True)
    fecha_hora = Column(DateTime, nullable=False)
    usuario = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "tabla_afectada": self.tabla_afectada,
            "registro_id": self.registro_id,
            "accion": self.accion,
            "detalles": self.detalles,
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "usuario": self.usuario
        }