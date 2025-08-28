from sqlalchemy import event, DDL
from src.cliente.cliModel import Cliente
from src.producto.prodModel import Producto
from src.pedidos.pedidoModel import Pedido
from src.empresa.empModel import Empresa
from src.documento.docModel import Documento
from src.documento.factura.facModel import Factura
from src.documento.notas.notaModel import NotaDebito, NotaCredito
from database import Base

# Función general para registrar auditoría
funcion_auditoria_general = DDL(
    """
CREATE OR REPLACE FUNCTION registrar_auditoria()
RETURNS TRIGGER AS $$
DECLARE
    registro_id INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        -- Intentar obtener el ID del registro eliminado
        BEGIN
            registro_id := OLD.id;
        EXCEPTION WHEN others THEN
            registro_id := NULL;
        END;
        IF registro_id IS NULL THEN
            registro_id := -1; -- Valor predeterminado para evitar violaciones de NOT NULL
        END IF;
        INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
        VALUES (
            TG_TABLE_NAME,  -- Nombre de la tabla afectada
            registro_id,    -- ID del registro eliminado o valor predeterminado
            TG_OP,          -- Operación (DELETE)
            row_to_json(OLD), -- Detalles del registro eliminado en formato JSON
            CURRENT_TIMESTAMP, -- Fecha y hora de la operación
            current_user    -- Usuario que ejecutó la operación
        );
    ELSE
        -- Intentar obtener el ID del registro afectado
        BEGIN
            registro_id := NEW.id;
        EXCEPTION WHEN others THEN
            registro_id := NULL;
        END;
        IF registro_id IS NULL THEN
            registro_id := -1; -- Valor predeterminado para evitar violaciones de NOT NULL
        END IF;
        INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
        VALUES (
            TG_TABLE_NAME,  -- Nombre de la tabla afectada
            registro_id,    -- ID del registro afectado o valor predeterminado
            TG_OP,          -- Operación (INSERT, UPDATE)
            row_to_json(NEW), -- Detalles del registro afectado en formato JSON
            CURRENT_TIMESTAMP, -- Fecha y hora de la operación
            current_user    -- Usuario que ejecutó la operación
        );
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""
)

# Definir el DDL para los triggers generales
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

trigger_auditoria_nota_debito = DDL(
    """
CREATE TRIGGER trigger_auditoria_nota_debito
AFTER INSERT OR UPDATE OR DELETE ON nota_debito
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

trigger_auditoria_nota_credito = DDL(
    """
CREATE TRIGGER trigger_auditoria_nota_credito
AFTER INSERT OR UPDATE OR DELETE ON nota_credito
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
"""
)

# Asociar las funciones y triggers con las tablas correspondientes
event.listen(Base.metadata, "before_create", funcion_auditoria_general)

event.listen(Cliente.__table__, "after_create", trigger_auditoria_cliente)
event.listen(Producto.__table__, "after_create", trigger_auditoria_producto)
event.listen(Pedido.__table__, "after_create", trigger_auditoria_pedido)
event.listen(Empresa.__table__, "after_create", trigger_auditoria_empresa)
event.listen(Documento.__table__, "after_create", trigger_auditoria_documento)
event.listen(Factura.__table__, "after_create", trigger_auditoria_factura)
event.listen(NotaDebito.__table__, "after_create", trigger_auditoria_nota_debito)
event.listen(NotaCredito.__table__, "after_create", trigger_auditoria_nota_credito)
