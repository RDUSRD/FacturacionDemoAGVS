from sqlalchemy import Column, Integer, JSON, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from src.documento.docModel import Documento


class NotaDebito(Documento):
    __tablename__ = "nota_debito"

    nota_debito_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)

    # Monto de la nota de débito
    monto_debito = Column(Float, nullable=False)

    # Descripción de la nota de débito
    descripcion = Column(String, nullable=False)

    # JSON para modificaciones generales del documento (subtotal, IVA, total, etc.)
    modif_documento = Column(JSON, nullable=True)

    # JSON para modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)
    modif_detalles = Column(JSON, nullable=True)

    # Relación hacia la factura original
    factura_id = Column(Integer, ForeignKey("factura.factura_id"), nullable=False)

    # Relación con el modelo Factura
    factura = relationship("Factura", backref="notas_debito", foreign_keys=[factura_id])

    __mapper_args__ = {
        "polymorphic_identity": "NotaDebito",
    }


class NotaCredito(Documento):
    __tablename__ = "nota_credito"

    nota_credito_id = Column(Integer, primary_key=True, autoincrement=True)
    documento_id = Column(Integer, ForeignKey("documento.id"), nullable=False)

    # Monto de la nota de crédito
    monto_credito = Column(Float, nullable=False)

    # Descripción de la nota de crédito
    descripcion = Column(String, nullable=False)

    # JSON para modificaciones generales del documento (subtotal, IVA, total, etc.)
    modif_documento = Column(JSON, nullable=True)

    # JSON para modificaciones en los detalles de la factura (productos, cantidades, descuentos, etc.)
    modif_detalles = Column(JSON, nullable=True)

    # Relación hacia la factura original
    factura_id = Column(Integer, ForeignKey("factura.factura_id"), nullable=False)

    # Relación con el modelo Factura
    factura = relationship("Factura", backref="notas_credito", foreign_keys=[factura_id])

    __mapper_args__ = {
        "polymorphic_identity": "NotaCredito",
    }
