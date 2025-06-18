from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.documento.docModel import Documento

class ComprobanteRetencion(Documento):
    __tablename__ = "comprobante_retencion"

    id = Column(Integer, ForeignKey("documento.id"), primary_key=True)
    documento_relacionado_id = Column(Integer, nullable=False)
    tipo_impuesto = Column(String(50), nullable=False)
    monto_retenido = Column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "comprobante_retencion"
    }
