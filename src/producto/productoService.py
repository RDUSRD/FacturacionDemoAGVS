from sqlalchemy.orm import Session
from src.producto.prodModel import Producto

def get_or_create_producto(db: Session, producto_data: dict):
    producto = db.query(Producto).filter(Producto.codigo == producto_data["codigo"]).first()
    if not producto:
        producto = Producto(**producto_data)
        db.add(producto)
        db.commit()
        db.refresh(producto)
    return producto
