from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

env = Environment(loader=FileSystemLoader("templates"))

def generate_pdf(document, document_type: str, transaction_data: Dict[str, Any]):
    template_name = {
        "factura": "factura_pdf.html",
        "debit_note": "debit_note_pdf.html",
        "credit_note": "credit_note_pdf.html",
        "delivery_order": "delivery_order_pdf.html",
        "retention_receipt": "retention_receipt_pdf.html",
    }[document_type]
    template = env.get_template(template_name)

    # Usar transaction_data directamente para el PDF
    html_content = template.render(**transaction_data)

    HTML(string=html_content).write_pdf(
        f"documents/{document_type}_{document.document_number}.pdf"
    )
