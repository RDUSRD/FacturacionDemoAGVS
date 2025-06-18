from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.producto.productoService import get_or_create_producto

router = APIRouter()

@router.post("/producto")
def create_or_get_producto(producto_data: dict, db: Session = Depends(get_db)):
    return get_or_create_producto(db, producto_data)
