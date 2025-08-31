from sqlalchemy.orm import Session
from src.cliente.cliModel import Cliente
from src.cliente.clienteSchema import ClienteSchema, ClienteUpdateSchema


def get_all_clientes(db: Session, limit: int = 10, page: int = 1):
    try:
        offset = (page - 1) * limit
        clientes = db.query(Cliente).offset(offset).limit(limit).all()
        return [cliente.to_dict() for cliente in clientes]
    except Exception as e:
        return f"Error al obtener clientes: {e}"


def get_cliente_by_id(db: Session, cliente_id: int):
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()

def get_cliente_by_documento(db: Session, documento: str):
    return db.query(Cliente).filter(Cliente.documento == documento).first()

def get_or_create_cliente(db: Session, cliente_data: ClienteSchema):
    cliente = db.query(Cliente).filter(Cliente.documento == cliente_data.documento).first()
    if not cliente:
        cliente = Cliente(**cliente_data.model_dump())
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente
    return {"message": "Cliente ya existe " + cliente.documento, "cliente": cliente}


def update_cliente(db: Session, cliente_id: int, cliente_data: ClienteUpdateSchema):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        for key, value in cliente_data.model_dump(exclude_unset=True).items():
            setattr(cliente, key, value)
        db.commit()
        db.refresh(cliente)
    return cliente


# def delete_cliente(db: Session, cliente_id: int):
#     cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
#     if cliente:
#         db.delete(cliente)
#         db.commit()
#     return cliente
