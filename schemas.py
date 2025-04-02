from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Literal, Optional, List, Dict

# EmisorBase: Esquema base con datos del emisor.
class EmisorBase(BaseModel):
    name: str
    fiscal_address: str
    rif: str

# ReceptorBase: Esquema base con datos del receptor (requiere rif o id_number).
class ReceptorBase(BaseModel):
    name: str
    fiscal_address: str
    rif: Optional[str] = None
    id_number: Optional[str] = None

    # check_identification: Valida que se proporcione por lo menos rif o id_number.
    @validator("id_number", always=True)
    def check_identification(cls, v, values):
        if not values.get("rif") and not v:
            raise ValueError("Se requiere RIF o número de identificación")
        return v

# Operation: Esquema para definir una operación o ítem en el documento.
class Operation(BaseModel):
    description: str
    code: str
    price: float
    quantity: Optional[int] = None
    is_exempt: bool = False

# DigitalPrinterBase: Esquema para los datos de la imprenta digital.
class DigitalPrinterBase(BaseModel):
    id: int
    name: str
    rif: str
    control_number_start: int
    control_number_end: int
    current_control_number: int
    authorization_nomenclature: str
    authorization_date: datetime

# FacturaCreate: Esquema para la creación de una factura.
class FacturaCreate(BaseModel):
    emisor: Optional[EmisorBase] = None
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    operations: List[Operation]
    digital_printer_id: int

# DebitNoteCreate: Esquema para la creación de una nota de débito.
class DebitNoteCreate(BaseModel):
    emisor: Optional[EmisorBase] = None
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    related_document_id: int
    operations: List[Operation]
    digital_printer_id: int

# CreditNoteCreate: Esquema para la creación de una nota de crédito.
class CreditNoteCreate(BaseModel):
    emisor: Optional[EmisorBase] = None
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    related_document_id: int
    operations: List[Operation]
    digital_printer_id: int

# DeliveryOrderCreate: Esquema para la creación de una orden de entrega.
class DeliveryOrderCreate(BaseModel):
    emisor: Optional[EmisorBase] = None
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    goods_delivered: List[str]
    digital_printer_id: int

# RetentionReceiptCreate: Esquema para la creación de un comprobante de retención.
class RetentionReceiptCreate(BaseModel):
    emisor: Optional[EmisorBase] = None
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    related_document_id: int
    tax_type: str
    retained_amount: float
    digital_printer_id: int

# DocumentResponse: Esquema de respuesta al retornar datos de un documento.
class DocumentResponse(BaseModel):
    id: int
    document_type: str
    document_number: int
    emisor: EmisorBase
    receptor: ReceptorBase
    issuance_date: datetime
    issuance_time: str
    control_number: int
    digital_printer: DigitalPrinterBase
    status: str

    class Config:
        from_attributes = True

# DefaultEmisorSchema: Esquema para definir el emisor predeterminado.
class DefaultEmisorSchema(BaseModel):
    name: str
    fiscal_address: str
    rif: str

    class Config:
        from_attributes = True

# AuditLogSchema: Esquema para registrar datos de auditoría.
class AuditLogSchema(BaseModel):
    id: int
    transaction_type: str
    transaction_data: Dict
    transaction_date: datetime
    client_ip: str

    class Config:
        from_attributes = True