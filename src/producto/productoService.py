from sqlalchemy.orm import Session
from src.producto.prodModel import Producto
from src.producto.productoSchema import ProductoSchema, ProductoUpdateSchema


def get_all_productos(db: Session):
    return db.query(Producto).all()


def get_producto_by_id(db: Session, producto_id: int):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def get_or_create_producto(db: Session, producto_data: ProductoSchema):
    producto = (
        db.query(Producto).filter(Producto.codigo == producto_data.codigo).first()
    )
    if not producto:
        producto = Producto(**producto_data.model_dump())
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