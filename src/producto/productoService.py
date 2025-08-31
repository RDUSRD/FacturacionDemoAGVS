from sqlalchemy.orm import Session
from src.producto.prodModel import Producto
from src.producto.productoSchema import ProductoSchema, ProductoUpdateSchema
import random


def get_all_productos(db: Session, limit: int = 10, offset: int = 0):
    return db.query(Producto).offset(offset).limit(limit).all()


def get_producto_by_id(db: Session, producto_id: int):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def get_producto_by_codigo(db: Session, codigo: str):
    return db.query(Producto).filter(Producto.codigo == codigo).first()


def get_producto_by_codigo_barras(db: Session, codigo_barras: str):
    return db.query(Producto).filter(Producto.codigo_barras == codigo_barras).first()


def get_producto_by_codigo_QR(db: Session, codigo_QR: str):
    return db.query(Producto).filter(Producto.codigo_QR == codigo_QR).first()


def get_producto_exento(db: Session):
    return db.query(Producto).filter(Producto.exento).all()


def generate_unique_codigo(db: Session) -> str:
    """Genera un código único de 8 dígitos como cadena para un producto."""
    while True:
        codigo = str(random.randint(10000000, 99999999))
        if not db.query(Producto).filter(Producto.codigo == codigo).first():
            return codigo


def get_or_create_producto(db: Session, producto_data: ProductoSchema):
    # Verificar si el producto ya existe por código
    producto = (
        db.query(Producto).filter(Producto.codigo == producto_data.codigo).first()
    )
    if not producto:
        # Crear el producto directamente, confiando en los valores predeterminados automáticos
        producto = Producto(**producto_data.model_dump())
        producto.codigo = generate_unique_codigo(db)
        producto.codigo_barras = generate_unique_codigo(db)
        producto.codigo_QR = generate_unique_codigo(db)
        db.add(producto)
        db.commit()
        db.refresh(producto)
        return producto
    return {"detail": "Producto ya existe.", "producto": producto}


def update_producto(db: Session, producto_id: int, producto_data: ProductoUpdateSchema):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto:
        for key, value in producto_data.model_dump(exclude_unset=True).items():
            setattr(producto, key, value)
        db.commit()
        db.refresh(producto)
    return producto
