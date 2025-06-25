from sqlalchemy import Column, Integer, Float, JSON, ForeignKey
from src.documento.docModel import Documento


class NotaDebito(Documento):
    __tablename__ = "nota_debito"

    nota_debito_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    documento_relacionado_id = Column(Integer, nullable=False)
    operaciones = Column(JSON, nullable=False)
    montos_base_iva = Column(JSON, nullable=False)
    monto_exento = Column(Float, nullable=False)
    montos_iva = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "Nota_debito",
    }


class NotaCredito(Documento):
    __tablename__ = "nota_credito"

    nota_credito_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)
    documento_relacionado_id = Column(Integer, nullable=False)
    operaciones = Column(JSON, nullable=False)
    montos_base_iva = Column(JSON, nullable=False)
    monto_exento = Column(Float, nullable=False)
    montos_iva = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "Nota_credito",
    }
