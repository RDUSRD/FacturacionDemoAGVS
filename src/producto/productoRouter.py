from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from src.producto.productoService import (
    get_producto_by_id,
    get_all_productos,
    get_or_create_producto,
    update_producto,
)
from src.producto.productoSchema import ProductoSchema, ProductoUpdateSchema

router = APIRouter(prefix="/producto", tags=["Producto"])


@router.get("/")
def get_productos(db: Session = Depends(get_db)):
    return get_all_productos(db)


@router.get("/{producto_id}")
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo/{codigo}")
def get_producto_by_codigo(codigo: str, db: Session = Depends(get_db)):
    producto = get_producto_by_codigo(db, codigo)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo_barras/{codigo_barras}")
def get_producto_by_codigo_barras(codigo_barras: str, db: Session = Depends(get_db)):
    producto = get_producto_by_codigo_barras(db, codigo_barras)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo_QR/{codigo_QR}")
def get_producto_by_codigo_QR(codigo_QR: str, db: Session = Depends(get_db)):
    producto = get_producto_by_codigo_QR(db, codigo_QR)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/exento")
def get_producto_exento(db: Session = Depends(get_db)):
    return get_producto_exento(db)


@router.post("/create")
def create_or_get_producto_endpoint(
    producto_data: ProductoSchema, db: Session = Depends(get_db)
):
    return get_or_create_producto(db, producto_data)


@router.put("/{producto_id}")
def update_producto_endpoint(
    producto_id: int, producto_data: ProductoUpdateSchema, db: Session = Depends(get_db)
):
    producto = update_producto(db, producto_id, producto_data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
