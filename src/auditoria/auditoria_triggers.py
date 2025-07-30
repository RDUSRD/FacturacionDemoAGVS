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
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        row_to_json(COALESCE(NEW, OLD)),
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

# Función para registrar auditoría de la tabla factura
funcion_auditoria_factura = DDL(
    """
CREATE OR REPLACE FUNCTION registrar_auditoria_factura()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
    VALUES (
        'factura',
        NEW.factura_id,
        TG_OP,
        row_to_json(NEW),
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

# Función para registrar auditoría de la tabla nota_debito
funcion_auditoria_nota_debito = DDL(
    """
CREATE OR REPLACE FUNCTION registrar_auditoria_nota_debito()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
    VALUES (
        'nota_debito',
        NEW.nota_debito_id,
        TG_OP,
        row_to_json(NEW),
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

# Función para registrar auditoría de la tabla nota_credito
funcion_auditoria_nota_credito = DDL(
    """
CREATE OR REPLACE FUNCTION registrar_auditoria_nota_credito()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
    VALUES (
        'nota_credito',
        NEW.nota_credito_id,
        TG_OP,
        row_to_json(NEW),
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
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

# Definir el DDL para los triggers específicos
trigger_auditoria_factura = DDL(
    """
CREATE TRIGGER trigger_auditoria_factura
AFTER INSERT OR UPDATE OR DELETE ON factura
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria_factura();
"""
)

trigger_auditoria_nota_debito = DDL(
    """
CREATE TRIGGER trigger_auditoria_nota_debito
AFTER INSERT OR UPDATE OR DELETE ON nota_debito
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria_nota_debito();
"""
)

trigger_auditoria_nota_credito = DDL(
    """
CREATE TRIGGER trigger_auditoria_nota_credito
AFTER INSERT OR UPDATE OR DELETE ON nota_credito
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria_nota_credito();
"""
)

# Asociar las funciones y triggers con las tablas correspondientes
event.listen(Base.metadata, "before_create", funcion_auditoria_general)
event.listen(Base.metadata, "before_create", funcion_auditoria_factura)
event.listen(Base.metadata, "before_create", funcion_auditoria_nota_debito)
event.listen(Base.metadata, "before_create", funcion_auditoria_nota_credito)

event.listen(Cliente.__table__, "after_create", trigger_auditoria_cliente)
event.listen(Producto.__table__, "after_create", trigger_auditoria_producto)
event.listen(Pedido.__table__, "after_create", trigger_auditoria_pedido)
event.listen(Empresa.__table__, "after_create", trigger_auditoria_empresa)
event.listen(Documento.__table__, "after_create", trigger_auditoria_documento)
event.listen(Factura.__table__, "after_create", trigger_auditoria_factura)
event.listen(NotaDebito.__table__, "after_create", trigger_auditoria_nota_debito)
event.listen(NotaCredito.__table__, "after_create", trigger_auditoria_nota_credito)
