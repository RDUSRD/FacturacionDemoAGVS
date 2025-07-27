from sqlalchemy import event, DDL
from src.cliente.cliModel import Cliente
from src.producto.prodModel import Producto
from src.pedidos.pedidoModel import Pedido
from src.empresa.empModel import Empresa
from src.documento.docModel import Documento
from src.documento.factura.facModel import Factura
from database import Base

# Definir el DDL para la función de auditoría
funcion_auditoria = DDL(
    """
CREATE OR REPLACE FUNCTION registrar_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
    VALUES (
        TG_TABLE_NAME,  -- Nombre de la tabla afectada
        NEW.id,         -- ID del registro afectado (asume que todas las tablas tienen una columna 'id')
        TG_OP,          -- Operación (INSERT, UPDATE, DELETE)
        row_to_json(NEW), -- Detalles del registro afectado en formato JSON
        CURRENT_TIMESTAMP, -- Fecha y hora de la operación
        current_user    -- Usuario que ejecutó la operación
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

# Asociar la creación de la función al evento 'before_create' de cualquier tabla
event.listen(Base.metadata, "before_create", funcion_auditoria)

# Definir el DDL para los triggers
trigger_auditoria_cliente = DDL(
    """
CREATE TRIGGER trigger_auditoria_cliente
AFTER INSERT OR UPDATE OR DELETE ON cliente
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_producto = DDL(
    """
CREATE TRIGGER trigger_auditoria_producto
AFTER INSERT OR UPDATE OR DELETE ON producto
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_pedido = DDL(
    """
CREATE TRIGGER trigger_auditoria_pedido
AFTER INSERT OR UPDATE OR DELETE ON pedido
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_empresa = DDL(
    """
CREATE TRIGGER trigger_auditoria_empresa
AFTER INSERT OR UPDATE OR DELETE ON empresa
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_documento = DDL(
    """
CREATE TRIGGER trigger_auditoria_documento
AFTER INSERT OR UPDATE OR DELETE ON documento
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_factura = DDL(
    """
CREATE TRIGGER trigger_auditoria_factura
AFTER INSERT OR UPDATE OR DELETE ON factura
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

# Asociar los triggers con las tablas correspondientes
event.listen(Cliente.__table__, "after_create", trigger_auditoria_cliente)
event.listen(Producto.__table__, "after_create", trigger_auditoria_producto)
event.listen(Pedido.__table__, "after_create", trigger_auditoria_pedido)
event.listen(Empresa.__table__, "after_create", trigger_auditoria_empresa)
event.listen(Documento.__table__, "after_create", trigger_auditoria_documento)
event.listen(Factura.__table__, "after_create", trigger_auditoria_factura)
