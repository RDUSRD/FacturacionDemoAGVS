from sqlalchemy.orm import Session
from models import Emisor, Receptor, DigitalPrinter, DocumentNumberSequence, Factura, DebitNote, CreditNote, DeliveryOrder, RetentionReceipt, DefaultEmisor, AuditLog
from schemas import FacturaCreate, DebitNoteCreate, CreditNoteCreate, DeliveryOrderCreate, RetentionReceiptCreate, DefaultEmisorSchema
from datetime import datetime
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates"))

class DocumentService:
    VAT_RATE = 0.16

    @staticmethod
    def get_or_create_emisor(db: Session, emisor_data: dict):
        emisor = db.query(Emisor).filter(Emisor.rif == emisor_data["rif"]).first()
        if not emisor:
            emisor = Emisor(**emisor_data)
            db.add(emisor)
            db.commit()
            db.refresh(emisor)
        return emisor

    @staticmethod
    def get_or_create_receptor(db: Session, receptor_data: dict):
        receptor = db.query(Receptor).filter(Receptor.rif == receptor_data["rif"]).first() if receptor_data.get("rif") else db.query(Receptor).filter(Receptor.id_number == receptor_data["id_number"]).first()
        if not receptor:
            receptor = Receptor(**receptor_data)
            db.add(receptor)
            db.commit()
            db.refresh(receptor)
        logger.debug(f"Receptor creado/recuperado: {receptor.name}, RIF: {receptor.rif}, ID: {receptor.id_number}")
        return receptor

    @staticmethod
    def get_next_number(db: Session, document_type: str):
        sequence = db.query(DocumentNumberSequence).filter(DocumentNumberSequence.document_type == document_type).first()
        if not sequence:
            sequence = DocumentNumberSequence(document_type=document_type, current_number=1)
            db.add(sequence)
        else:
            sequence.current_number += 1
        db.commit()
        return sequence.current_number

    @staticmethod
    def get_next_control_number(db: Session, digital_printer_id: int):
        printer = db.query(DigitalPrinter).filter(DigitalPrinter.id == digital_printer_id).first()
        if printer.current_control_number < printer.control_number_end:
            printer.current_control_number += 1
            db.commit()
            return printer.current_control_number
        raise ValueError("Rango de números de control agotado")

    @staticmethod
    def calculate_financial_totals(operations: List[dict], is_credit_note: bool = False):
        vat_base_amounts = {}
        total_exempt_amount = 0.0
        vat_amounts = {}
        total_value = 0.0

        for op in operations:
            quantity = op.get("quantity", 1)
            subtotal = op["price"] * quantity * (-1 if is_credit_note else 1)
            if op["is_exempt"]:
                total_exempt_amount += subtotal
            else:
                vat_base_amounts["16%"] = vat_base_amounts.get("16%", 0) + subtotal
                vat_amount = subtotal * DocumentService.VAT_RATE
                vat_amounts["16%"] = vat_amounts.get("16%", 0) + vat_amount
            total_value += subtotal + (vat_amount if not op["is_exempt"] else 0)

        total_value += total_exempt_amount
        return vat_base_amounts, total_exempt_amount, vat_amounts, total_value

    @staticmethod
    def get_default_emisor(db: Session):
        default_emisor = db.query(DefaultEmisor).first()
        if not default_emisor:
            default_emisor = DefaultEmisor(name="Default Emisor", fiscal_address="Default Address", rif="J-00000000-0")
            db.add(default_emisor)
            db.commit()
            db.refresh(default_emisor)
        return default_emisor

    @staticmethod
    def update_default_emisor(db: Session, emisor_data: DefaultEmisorSchema):
        default_emisor = db.query(DefaultEmisor).first()
        if default_emisor:
            default_emisor.name = emisor_data.name
            default_emisor.fiscal_address = emisor_data.fiscal_address
            default_emisor.rif = emisor_data.rif
        else:
            default_emisor = DefaultEmisor(**emisor_data.dict())
            db.add(default_emisor)
        db.commit()
        db.refresh(default_emisor)
        return default_emisor

    @staticmethod
    def serialize_transaction_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte objetos datetime en cadenas ISO para hacerlos serializables a JSON."""
        serialized_data = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                serialized_data[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized_data[key] = DocumentService.serialize_transaction_data(value)
            elif isinstance(value, list):
                serialized_data[key] = [DocumentService.serialize_transaction_data(item) if isinstance(item, dict) else item for item in value]
            else:
                serialized_data[key] = value
        return serialized_data

    @staticmethod
    def log_transaction(db: Session, transaction_type: str, transaction_data: dict, client_ip: str):
        serialized_data = DocumentService.serialize_transaction_data(transaction_data)
        audit_entry = AuditLog(
            transaction_type=transaction_type,
            transaction_data=serialized_data,
            transaction_date=datetime.now(),
            client_ip=client_ip
        )
        db.add(audit_entry)
        db.commit()
        logger.debug(f"Registrada transacción en auditoría: {transaction_type}, IP: {client_ip}")

    @staticmethod
    def create_factura(db: Session, factura: FacturaCreate, client_ip: str):
        default_emisor = DocumentService.get_default_emisor(db)
        emisor_data = factura.emisor.dict() if factura.emisor else {
            "name": default_emisor.name,
            "fiscal_address": default_emisor.fiscal_address,
            "rif": default_emisor.rif
        }
        emisor = DocumentService.get_or_create_emisor(db, emisor_data)
        receptor = DocumentService.get_or_create_receptor(db, factura.receptor.dict())
        document_number = DocumentService.get_next_number(db, "factura")
        control_number = DocumentService.get_next_control_number(db, factura.digital_printer_id)

        vat_base_amounts, total_exempt_amount, vat_amounts, total_value = DocumentService.calculate_financial_totals(
            [op.dict() for op in factura.operations]
        )

        db_factura = Factura(
            document_type="factura",
            document_number=document_number,
            emisor_id=emisor.id,
            receptor_id=receptor.id,
            issuance_date=factura.issuance_date,
            issuance_time=factura.issuance_time,
            digital_printer_id=factura.digital_printer_id,
            control_number=control_number,
            control_number_assignment_date=datetime.now(),
            operations=[op.dict() for op in factura.operations],
            vat_base_amounts=vat_base_amounts,
            total_exempt_amount=total_exempt_amount,
            vat_amounts=vat_amounts,
            total_value=total_value,
        )
        db.add(db_factura)
        db.commit()
        db.refresh(db_factura)

        # Verificar datos antes de guardar
        logger.debug(f"Datos de db_factura: emisor_id={db_factura.emisor_id}, receptor_id={db_factura.receptor_id}, operations={db_factura.operations}")

        # Construir transaction_data completo
        transaction_data = factura.dict()
        transaction_data.update({
            "document_type": "Factura",
            "emisor": emisor_data,
            "document_number": document_number,
            "control_number": control_number,
            "digital_printer": {
                "id": db_factura.digital_printer.id,
                "name": db_factura.digital_printer.name,
                "rif": db_factura.digital_printer.rif,
                "control_number_start": db_factura.digital_printer.control_number_start,
                "control_number_end": db_factura.digital_printer.control_number_end,
                "current_control_number": db_factura.digital_printer.current_control_number,
                "authorization_nomenclature": db_factura.digital_printer.authorization_nomenclature,
                "authorization_date": db_factura.digital_printer.authorization_date
            },
            "vat_base_amounts": vat_base_amounts,
            "total_exempt_amount": total_exempt_amount,
            "vat_amounts": vat_amounts,
            "total_value": total_value
        })
        DocumentService.log_transaction(db, "create_factura", transaction_data, client_ip)
        DocumentService.generate_pdf(db_factura, "factura", transaction_data)
        return db_factura

    @staticmethod
    def create_debit_note(db: Session, debit_note: DebitNoteCreate, client_ip: str):
        default_emisor = DocumentService.get_default_emisor(db)
        emisor_data = debit_note.emisor.dict() if debit_note.emisor else {
            "name": default_emisor.name,
            "fiscal_address": default_emisor.fiscal_address,
            "rif": default_emisor.rif
        }
        emisor = DocumentService.get_or_create_emisor(db, emisor_data)
        receptor = DocumentService.get_or_create_receptor(db, debit_note.receptor.dict())
        document_number = DocumentService.get_next_number(db, "debit_note")
        control_number = DocumentService.get_next_control_number(db, debit_note.digital_printer_id)

        vat_base_amounts, total_exempt_amount, vat_amounts, total_value = DocumentService.calculate_financial_totals(
            [op.dict() for op in debit_note.operations]
        )

        db_debit_note = DebitNote(
            document_type="debit_note",
            document_number=document_number,
            emisor_id=emisor.id,
            receptor_id=receptor.id,
            issuance_date=debit_note.issuance_date,
            issuance_time=debit_note.issuance_time,
            digital_printer_id=debit_note.digital_printer_id,
            control_number=control_number,
            control_number_assignment_date=datetime.now(),
            related_document_id=debit_note.related_document_id,
            operations=[op.dict() for op in debit_note.operations],
            vat_base_amounts=vat_base_amounts,
            total_exempt_amount=total_exempt_amount,
            vat_amounts=vat_amounts,
            total_value=total_value,
        )
        db.add(db_debit_note)
        db.commit()
        db.refresh(db_debit_note)

        # Construir transaction_data completo
        transaction_data = debit_note.dict()
        transaction_data.update({
            "document_type": "Nota de Débito",
            "emisor": emisor_data,
            "document_number": document_number,
            "control_number": control_number,
            "digital_printer": {
                "id": db_debit_note.digital_printer.id,
                "name": db_debit_note.digital_printer.name,
                "rif": db_debit_note.digital_printer.rif,
                "control_number_start": db_debit_note.digital_printer.control_number_start,
                "control_number_end": db_debit_note.digital_printer.control_number_end,
                "current_control_number": db_debit_note.digital_printer.current_control_number,
                "authorization_nomenclature": db_debit_note.digital_printer.authorization_nomenclature,
                "authorization_date": db_debit_note.digital_printer.authorization_date
            },
            "vat_base_amounts": vat_base_amounts,
            "total_exempt_amount": total_exempt_amount,
            "vat_amounts": vat_amounts,
            "total_value": total_value
        })
        DocumentService.log_transaction(db, "create_debit_note", transaction_data, client_ip)
        DocumentService.generate_pdf(db_debit_note, "debit_note", transaction_data)
        return db_debit_note

    @staticmethod
    def create_credit_note(db: Session, credit_note: CreditNoteCreate, client_ip: str):
        default_emisor = DocumentService.get_default_emisor(db)
        emisor_data = credit_note.emisor.dict() if credit_note.emisor else {
            "name": default_emisor.name,
            "fiscal_address": default_emisor.fiscal_address,
            "rif": default_emisor.rif
        }
        emisor = DocumentService.get_or_create_emisor(db, emisor_data)
        receptor = DocumentService.get_or_create_receptor(db, credit_note.receptor.dict())
        document_number = DocumentService.get_next_number(db, "credit_note")
        control_number = DocumentService.get_next_control_number(db, credit_note.digital_printer_id)

        vat_base_amounts, total_exempt_amount, vat_amounts, total_value = DocumentService.calculate_financial_totals(
            [op.dict() for op in credit_note.operations], is_credit_note=True
        )

        db_credit_note = CreditNote(
            document_type="credit_note",
            document_number=document_number,
            emisor_id=emisor.id,
            receptor_id=receptor.id,
            issuance_date=credit_note.issuance_date,
            issuance_time=credit_note.issuance_time,
            digital_printer_id=credit_note.digital_printer_id,
            control_number=control_number,
            control_number_assignment_date=datetime.now(),
            related_document_id=credit_note.related_document_id,
            operations=[op.dict() for op in credit_note.operations],
            vat_base_amounts=vat_base_amounts,
            total_exempt_amount=total_exempt_amount,
            vat_amounts=vat_amounts,
            total_value=total_value,
        )
        db.add(db_credit_note)
        db.commit()
        db.refresh(db_credit_note)

        # Construir transaction_data completo
        transaction_data = credit_note.dict()
        transaction_data.update({
            "document_type": "Nota de Crédito",
            "emisor": emisor_data,
            "document_number": document_number,
            "control_number": control_number,
            "digital_printer": {
                "id": db_credit_note.digital_printer.id,
                "name": db_credit_note.digital_printer.name,
                "rif": db_credit_note.digital_printer.rif,
                "control_number_start": db_credit_note.digital_printer.control_number_start,
                "control_number_end": db_credit_note.digital_printer.control_number_end,
                "current_control_number": db_credit_note.digital_printer.current_control_number,
                "authorization_nomenclature": db_credit_note.digital_printer.authorization_nomenclature,
                "authorization_date": db_credit_note.digital_printer.authorization_date
            },
            "vat_base_amounts": vat_base_amounts,
            "total_exempt_amount": total_exempt_amount,
            "vat_amounts": vat_amounts,
            "total_value": total_value
        })
        DocumentService.log_transaction(db, "create_credit_note", transaction_data, client_ip)
        DocumentService.generate_pdf(db_credit_note, "credit_note", transaction_data)
        return db_credit_note

    @staticmethod
    def create_delivery_order(db: Session, delivery_order: DeliveryOrderCreate, client_ip: str):
        default_emisor = DocumentService.get_default_emisor(db)
        emisor_data = delivery_order.emisor.dict() if delivery_order.emisor else {
            "name": default_emisor.name,
            "fiscal_address": default_emisor.fiscal_address,
            "rif": default_emisor.rif
        }
        emisor = DocumentService.get_or_create_emisor(db, emisor_data)
        receptor = DocumentService.get_or_create_receptor(db, delivery_order.receptor.dict())
        document_number = DocumentService.get_next_number(db, "delivery_order")
        control_number = DocumentService.get_next_control_number(db, delivery_order.digital_printer_id)

        db_delivery_order = DeliveryOrder(
            document_type="delivery_order",
            document_number=document_number,
            emisor_id=emisor.id,
            receptor_id=receptor.id,
            issuance_date=delivery_order.issuance_date,
            issuance_time=delivery_order.issuance_time,
            digital_printer_id=delivery_order.digital_printer_id,
            control_number=control_number,
            control_number_assignment_date=datetime.now(),
            goods_delivered=delivery_order.goods_delivered,
        )
        db.add(db_delivery_order)
        db.commit()
        db.refresh(db_delivery_order)

        # Construir transaction_data completo
        transaction_data = delivery_order.dict()
        transaction_data.update({
            "document_type": "Orden de Entrega",
            "emisor": emisor_data,
            "document_number": document_number,
            "control_number": control_number,
            "digital_printer": {
                "id": db_delivery_order.digital_printer.id,
                "name": db_delivery_order.digital_printer.name,
                "rif": db_delivery_order.digital_printer.rif,
                "control_number_start": db_delivery_order.digital_printer.control_number_start,
                "control_number_end": db_delivery_order.digital_printer.control_number_end,
                "current_control_number": db_delivery_order.digital_printer.current_control_number,
                "authorization_nomenclature": db_delivery_order.digital_printer.authorization_nomenclature,
                "authorization_date": db_delivery_order.digital_printer.authorization_date
            }
        })
        DocumentService.log_transaction(db, "create_delivery_order", transaction_data, client_ip)
        DocumentService.generate_pdf(db_delivery_order, "delivery_order", transaction_data)
        return db_delivery_order

    @staticmethod
    def create_retention_receipt(db: Session, retention_receipt: RetentionReceiptCreate, client_ip: str):
        default_emisor = DocumentService.get_default_emisor(db)
        emisor_data = retention_receipt.emisor.dict() if retention_receipt.emisor else {
            "name": default_emisor.name,
            "fiscal_address": default_emisor.fiscal_address,
            "rif": default_emisor.rif
        }
        emisor = DocumentService.get_or_create_emisor(db, emisor_data)
        receptor = DocumentService.get_or_create_receptor(db, retention_receipt.receptor.dict())
        document_number = DocumentService.get_next_number(db, "retention_receipt")
        control_number = DocumentService.get_next_control_number(db, retention_receipt.digital_printer_id)

        db_retention_receipt = RetentionReceipt(
            document_type="retention_receipt",
            document_number=document_number,
            emisor_id=emisor.id,
            receptor_id=receptor.id,
            issuance_date=retention_receipt.issuance_date,
            issuance_time=retention_receipt.issuance_time,
            digital_printer_id=retention_receipt.digital_printer_id,
            control_number=control_number,
            control_number_assignment_date=datetime.now(),
            related_document_id=retention_receipt.related_document_id,
            tax_type=retention_receipt.tax_type,
            retained_amount=retention_receipt.retained_amount,
        )
        db.add(db_retention_receipt)
        db.commit()
        db.refresh(db_retention_receipt)

        # Construir transaction_data completo
        transaction_data = retention_receipt.dict()
        transaction_data.update({
            "document_type": "Comprobante de Retención",
            "emisor": emisor_data,
            "document_number": document_number,
            "control_number": control_number,
            "digital_printer": {
                "id": db_retention_receipt.digital_printer.id,
                "name": db_retention_receipt.digital_printer.name,
                "rif": db_retention_receipt.digital_printer.rif,
                "control_number_start": db_retention_receipt.digital_printer.control_number_start,
                "control_number_end": db_retention_receipt.digital_printer.control_number_end,
                "current_control_number": db_retention_receipt.digital_printer.current_control_number,
                "authorization_nomenclature": db_retention_receipt.digital_printer.authorization_nomenclature,
                "authorization_date": db_retention_receipt.digital_printer.authorization_date
            }
        })
        DocumentService.log_transaction(db, "create_retention_receipt", transaction_data, client_ip)
        DocumentService.generate_pdf(db_retention_receipt, "retention_receipt", transaction_data)
        return db_retention_receipt

    @staticmethod
    def generate_pdf(document, document_type, transaction_data: Dict[str, Any]):
        template_name = {
            "factura": "factura_pdf.html",
            "debit_note": "debit_note_pdf.html",
            "credit_note": "credit_note_pdf.html",
            "delivery_order": "delivery_order_pdf.html",
            "retention_receipt": "retention_receipt_pdf.html",
        }[document_type]
        template = env.get_template(template_name)
        
        # Usar transaction_data directamente para el PDF
        data = DocumentService.serialize_transaction_data(transaction_data)
        logger.debug(f"Datos enviados a la plantilla {template_name}: {data}")
        html_content = template.render(**data)
        logger.debug(f"HTML generado: {html_content}")

        HTML(string=html_content).write_pdf(f"documents/{document_type}_{document.document_number}.pdf")