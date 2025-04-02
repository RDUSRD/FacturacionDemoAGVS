from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from database import Base

# Emisor: Modelo para representar al emisor de documentos.
class Emisor(Base):
    __tablename__ = "emisors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fiscal_address = Column(String, nullable=False)
    rif = Column(String, unique=True, nullable=False)
    documents = relationship("Document", back_populates="emisor")

# Receptor: Modelo para representar al receptor de documentos.
class Receptor(Base):
    __tablename__ = "receptors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fiscal_address = Column(String, nullable=False)
    rif = Column(String, unique=True, nullable=True)
    id_number = Column(String, unique=True, nullable=True)
    documents = relationship("Document", back_populates="receptor")

# DigitalPrinter: Modelo para la imprenta digital.
class DigitalPrinter(Base):
    __tablename__ = "digital_printers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rif = Column(String, unique=True, nullable=False)
    control_number_start = Column(Integer, nullable=False)
    control_number_end = Column(Integer, nullable=False)
    current_control_number = Column(Integer, nullable=False)
    authorization_nomenclature = Column(String, nullable=False)
    authorization_date = Column(DateTime, nullable=False)
    documents = relationship("Document", back_populates="digital_printer")

# DocumentNumberSequence: Modelo para llevar la secuencia de números de documentos.
class DocumentNumberSequence(Base):
    __tablename__ = "document_number_sequences"
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String, unique=True, nullable=False)
    current_number = Column(Integer, nullable=False)

# DefaultEmisor: Modelo para almacenar el emisor predeterminado.
class DefaultEmisor(Base):
    __tablename__ = "default_emisor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    fiscal_address = Column(String, nullable=False)
    rif = Column(String, unique=True, nullable=False)

# AuditLog: Modelo para registrar las entradas de auditoría.
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String, nullable=False)  # Tipo de transacción (ej., "create_factura")
    transaction_data = Column(JSON, nullable=False)      # Datos enviados en la transacción
    transaction_date = Column(DateTime, nullable=False)    # Fecha y hora de la transacción
    client_ip = Column(String, nullable=False)           # IP del cliente

# Document: Modelo base polimórfico para todos los documentos.
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String, nullable=False)
    document_number = Column(Integer, nullable=False, index=True)
    emisor_id = Column(Integer, ForeignKey("emisors.id"), nullable=False)
    receptor_id = Column(Integer, ForeignKey("receptors.id"), nullable=False)
    issuance_date = Column(DateTime, nullable=False)
    issuance_time = Column(String, nullable=False)
    digital_printer_id = Column(Integer, ForeignKey("digital_printers.id"), nullable=False)
    control_number = Column(Integer, nullable=False)
    control_number_assignment_date = Column(DateTime, nullable=False)
    status = Column(String, default="active")

    emisor = relationship("Emisor", back_populates="documents")
    receptor = relationship("Receptor", back_populates="documents")
    digital_printer = relationship("DigitalPrinter", back_populates="documents")

    __mapper_args__ = {
        "polymorphic_identity": "document",
        "polymorphic_on": document_type,
    }

# Factura: Modelo para representar una factura.
class Factura(Document):
    __tablename__ = "facturas"
    id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    operations = Column(JSON, nullable=False)
    vat_base_amounts = Column(JSON, nullable=False)
    total_exempt_amount = Column(Float, nullable=False)
    vat_amounts = Column(JSON, nullable=False)
    total_value = Column(Float, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "factura"}

# DebitNote: Modelo para representar una nota de débito.
class DebitNote(Document):
    __tablename__ = "debit_notes"
    id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    related_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    operations = Column(JSON, nullable=False)
    vat_base_amounts = Column(JSON, nullable=False)
    total_exempt_amount = Column(Float, nullable=False)
    vat_amounts = Column(JSON, nullable=False)
    total_value = Column(Float, nullable=False)

    related_document = relationship("Document", foreign_keys=[related_document_id])
    __mapper_args__ = {
        "polymorphic_identity": "debit_note",
        "inherit_condition": (id == Document.id),
    }

# CreditNote: Modelo para representar una nota de crédito.
class CreditNote(Document):
    __tablename__ = "credit_notes"
    id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    related_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    operations = Column(JSON, nullable=False)
    vat_base_amounts = Column(JSON, nullable=False)
    total_exempt_amount = Column(Float, nullable=False)
    vat_amounts = Column(JSON, nullable=False)
    total_value = Column(Float, nullable=False)

    related_document = relationship("Document", foreign_keys=[related_document_id])
    __mapper_args__ = {
        "polymorphic_identity": "credit_note",
        "inherit_condition": (id == Document.id),
    }

# DeliveryOrder: Modelo para representar una orden de entrega.
class DeliveryOrder(Document):
    __tablename__ = "delivery_orders"
    id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    goods_delivered = Column(JSON, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "delivery_order"}

# RetentionReceipt: Modelo para representar un comprobante de retención.
class RetentionReceipt(Document):
    __tablename__ = "retention_receipts"
    id = Column(Integer, ForeignKey("documents.id"), primary_key=True)
    related_document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    tax_type = Column(String, nullable=False)
    retained_amount = Column(Float, nullable=False)

    related_document = relationship("Document", foreign_keys=[related_document_id])
    __mapper_args__ = {
        "polymorphic_identity": "retention_receipt",
        "inherit_condition": (id == Document.id),
    }