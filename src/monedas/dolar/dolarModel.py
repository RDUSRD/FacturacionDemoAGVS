from sqlalchemy import Column, Integer, Float, Date, DateTime
from datetime import datetime
from database import Base


class Dolar(Base):
    __tablename__ = "dolar"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, default=datetime.today().date, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
