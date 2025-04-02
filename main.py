from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import FacturaCreate, DebitNoteCreate, CreditNoteCreate, DeliveryOrderCreate, RetentionReceiptCreate, DocumentResponse, DefaultEmisorSchema
from services import DocumentService
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from models import DigitalPrinter, Document, Receptor, AuditLog
from datetime import datetime
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    printer = db.query(DigitalPrinter).first()
    if not printer:
        printer = DigitalPrinter(
            name="Imprenta Digital Ejemplo",
            rif="J-12345678-9",
            control_number_start=1,
            control_number_end=1000,
            current_control_number=0,
            authorization_nomenclature="PA-2025-001",
            authorization_date=datetime.now(),
        )
        db.add(printer)
        db.commit()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(NoCacheMiddleware)
app.mount("/documents", StaticFiles(directory="documents"), name="documents")
app.mount("/static", StaticFiles(directory="static", html=True, check_dir=False), name="static")
env = Environment(loader=FileSystemLoader("templates"))

Base.metadata.create_all(bind=engine)

# Endpoints de creación
@app.post("/facturas/", response_model=DocumentResponse)
def create_factura(request: Request, factura: FacturaCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    return DocumentService.create_factura(db, factura, client_ip)

@app.post("/debit_notes/", response_model=DocumentResponse)
def create_debit_note(request: Request, debit_note: DebitNoteCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    return DocumentService.create_debit_note(db, debit_note, client_ip)

@app.post("/credit_notes/", response_model=DocumentResponse)
def create_credit_note(request: Request, credit_note: CreditNoteCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    return DocumentService.create_credit_note(db, credit_note, client_ip)

@app.post("/delivery_orders/", response_model=DocumentResponse)
def create_delivery_order(request: Request, delivery_order: DeliveryOrderCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    return DocumentService.create_delivery_order(db, delivery_order, client_ip)

@app.post("/retention_receipts/", response_model=DocumentResponse)
def create_retention_receipt(request: Request, retention_receipt: RetentionReceiptCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    return DocumentService.create_retention_receipt(db, retention_receipt, client_ip)

# Rutas de frontend
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    template = env.get_template("index.html")
    return template.render()

@app.get("/factura", response_class=HTMLResponse)
async def factura_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("factura.html")
    return template.render(default_emisor=default_emisor)

@app.get("/debit_note", response_class=HTMLResponse)
async def debit_note_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("debit_note.html")
    return template.render(default_emisor=default_emisor)

@app.get("/credit_note", response_class=HTMLResponse)
async def credit_note_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("credit_note.html")
    return template.render(default_emisor=default_emisor)

@app.get("/delivery_order", response_class=HTMLResponse)
async def delivery_order_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("delivery_order.html")
    return template.render(default_emisor=default_emisor)

@app.get("/retention_receipt", response_class=HTMLResponse)
async def retention_receipt_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("retention_receipt.html")
    return template.render(default_emisor=default_emisor)

@app.get("/documents", response_class=HTMLResponse)
async def get_documents(
    request: Request,
    document_type: Optional[str] = None,
    document_number: Optional[str] = None,
    receptor_rif: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if document_type == "":
        document_type = None
    if receptor_rif == "":
        receptor_rif = None
    
    document_number_int = None
    if document_number and document_number.strip():
        try:
            document_number_int = int(document_number)
        except ValueError:
            pass

    query = db.query(Document)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if document_number_int is not None:
        query = query.filter(Document.document_number == document_number_int)
    if receptor_rif:
        query = query.join(Document.receptor).filter(Receptor.rif == receptor_rif)
    
    documents = query.all()
    for doc in documents:
        logger.debug(f"Documento recuperado: {doc.document_type}, {doc.document_number}, Emisor: {doc.emisor.name}, Receptor: {doc.receptor.name}, RIF: {doc.receptor.rif}, ID: {doc.receptor.id_number}")
    template = env.get_template("documents.html")
    return template.render(documents=documents)

@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance_form(request: Request, db: Session = Depends(get_db)):
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("maintenance.html")
    return template.render(default_emisor=default_emisor)

@app.post("/maintenance/update_emisor", response_class=HTMLResponse)
async def update_default_emisor(request: Request, emisor: DefaultEmisorSchema, db: Session = Depends(get_db)):
    DocumentService.update_default_emisor(db, emisor)
    default_emisor = DocumentService.get_default_emisor(db)
    template = env.get_template("maintenance.html")
    return template.render(default_emisor=default_emisor, message="Datos del emisor actualizados con éxito")

@app.get("/audit_logs", response_class=HTMLResponse)
async def get_audit_logs(request: Request, db: Session = Depends(get_db)):
    audit_logs = db.query(AuditLog).order_by(AuditLog.transaction_date.desc()).all()
    template = env.get_template("audit_logs.html")
    return template.render(audit_logs=audit_logs)