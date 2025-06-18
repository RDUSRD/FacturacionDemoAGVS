"""
main.py
Este archivo es el punto de entrada para la aplicación FastAPI. Configura middleware, rutas y la inicialización de la base de datos.

Características:
- Middleware para gestión de sesiones y caché.
- Servir archivos estáticos y plantillas.
- Inicialización de datos predeterminados en la base de datos.

Dependencias:
- fastapi: Para construir la aplicación web.
- sqlalchemy: Para interacción con la base de datos.
- dotenv: Para gestión de variables de entorno.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from loggers.logger import app_logger
import os
from dotenv import load_dotenv

# Importar routers
from src.empresa.empresaRouter import router as empresa_router
from src.cliente.clienteRouter import router as cliente_router
from src.documento.documentoRouter import router as documento_router
from src.factura.facturaRouter import router as factura_router
from src.notas.notaRouter import router as nota_router
from src.orden_entrega.ordenEntregaRouter import router as orden_entrega_router
from src.comprobante_retencion.comprobanteRetencionRouter import router as comprobante_retencion_router
from src.producto.productoRouter import router as producto_router
from src.detalleFactura.detalleFacturaRouter import router as detalle_factura_router
from src.auditoria.audRouter import router as auditoria_router

# Cargar variables de entorno
load_dotenv()

# Configurar la aplicación FastAPI
app = FastAPI()

# Middleware para servir archivos estáticos
app.mount("/documents", StaticFiles(directory="documents"), name="documents")
app.mount("/static", StaticFiles(directory="static", html=True, check_dir=False), name="static")

# Incluir routers
app.include_router(empresa_router, prefix="/api/empresa")
app.include_router(cliente_router, prefix="/api/cliente")
app.include_router(documento_router, prefix="/api/documento")
app.include_router(factura_router, prefix="/api/factura")
app.include_router(nota_router, prefix="/api/nota")
app.include_router(orden_entrega_router, prefix="/api/orden_entrega")
app.include_router(comprobante_retencion_router, prefix="/api/comprobante_retencion")
app.include_router(producto_router, prefix="/api/producto")
app.include_router(detalle_factura_router, prefix="/api/detalle_factura")
app.include_router(auditoria_router, prefix="/api/auditoria")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Registrar un log al iniciar la aplicación
app_logger.info("Aplicación FastAPI iniciada correctamente")

