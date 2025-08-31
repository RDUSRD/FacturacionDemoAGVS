from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from database import get_db
from src.producto.productoService import (
    get_producto_by_id,
    get_all_productos,
    get_or_create_producto,
    update_producto,
    get_producto_by_codigo,
    get_producto_by_codigo_barras,
    get_producto_by_codigo_QR,
    get_producto_exento,
)
from src.producto.productoSchema import ProductoSchema, ProductoUpdateSchema
from src.loggers.loggerService import get_logger, get_request_info

logger = get_logger("ProductoRouter")

router = APIRouter(prefix="/producto", tags=["Producto"])


@router.get("/")
def get_productos(
    request: Request, db: Session = Depends(get_db), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)
):
    request_info = get_request_info(request)
    logger.info("Obteniendo todos los productos", extra=request_info)
    productos = get_all_productos(db, limit=limit, offset=offset)
    if not productos:
        logger.warning("No se encontraron productos", extra=request_info)
        raise HTTPException(status_code=404, detail="No se encontraron productos")
    return productos


@router.get("/{producto_id}")
def get_producto(producto_id: int, request: Request, db: Session = Depends(get_db)):
    request_info = get_request_info(request)
    logger.info(f"Obteniendo producto con ID: {producto_id}", extra=request_info)
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        logger.warning(f"Producto con ID: {producto_id} no encontrado", extra=request_info)
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo/{codigo}")
def get_producto_by_codigo_router(codigo: str, db: Session = Depends(get_db)):
    producto = get_producto_by_codigo(db, codigo)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo_barras/{codigo_barras}")
def get_producto_by_codigo_barras_router(
    codigo_barras: str, db: Session = Depends(get_db)
):
    producto = get_producto_by_codigo_barras(db, codigo_barras)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/codigo_QR/{codigo_QR}")
def get_producto_by_codigo_QR_router(codigo_QR: str, db: Session = Depends(get_db)):
    producto = get_producto_by_codigo_QR(db, codigo_QR)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/exento")
def get_producto_exento_router(db: Session = Depends(get_db)):
    return get_producto_exento(db)


@router.post("/create")
def create_or_get_producto_endpoint(
    producto_data: ProductoSchema, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info("Creando o obteniendo producto", extra=request_info)
    return get_or_create_producto(db, producto_data)


@router.put("/{producto_id}")
def update_producto_endpoint(
    producto_id: int, producto_data: ProductoUpdateSchema, request: Request, db: Session = Depends(get_db)
):
    request_info = get_request_info(request)
    logger.info(f"Actualizando producto con ID: {producto_id}", extra=request_info)
    producto = update_producto(db, producto_id, producto_data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
