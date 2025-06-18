from sqlalchemy.orm import Session
from src.cliente.cliModel import Cliente

def get_or_create_cliente(db: Session, cliente_data: dict):
    cliente = db.query(Cliente).filter(Cliente.rif == cliente_data["rif"]).first()
    if not cliente:
        cliente = Cliente(**cliente_data)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return cliente
