-- Crear la función de auditoría
CREATE OR REPLACE FUNCTION registrar_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
        VALUES (
            TG_TABLE_NAME,  -- Nombre de la tabla afectada
            OLD.id,         -- ID del registro eliminado (usando OLD)
            TG_OP,          -- Operación (DELETE)
            row_to_json(OLD), -- Detalles del registro eliminado en formato JSON
            CURRENT_TIMESTAMP, -- Fecha y hora de la operación
            current_user    -- Usuario que ejecutó la operación
        );
    ELSE
        INSERT INTO auditoria (tabla_afectada, registro_id, accion, detalles, fecha_hora, usuario)
        VALUES (
            TG_TABLE_NAME,  -- Nombre de la tabla afectada
            NEW.id,         -- ID del registro afectado (usando NEW para INSERT o UPDATE)
            TG_OP,          -- Operación (INSERT, UPDATE)
            row_to_json(NEW), -- Detalles del registro afectado en formato JSON
            CURRENT_TIMESTAMP, -- Fecha y hora de la operación
            current_user    -- Usuario que ejecutó la operación
        );
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Crear triggers para las tablas que deseas auditar
-- Trigger para la tabla 'cliente'
CREATE TRIGGER trigger_auditoria_cliente
AFTER INSERT OR UPDATE OR DELETE ON cliente
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();

-- Trigger para la tabla 'producto'
CREATE TRIGGER trigger_auditoria_producto
AFTER INSERT OR UPDATE OR DELETE ON producto
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();

-- Trigger para la tabla 'pedido'
CREATE TRIGGER trigger_auditoria_pedido
AFTER INSERT OR UPDATE OR DELETE ON pedido
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();

-- Trigger para la tabla empresa
CREATE TRIGGER trigger_auditoria_empresa
AFTER INSERT OR UPDATE OR DELETE ON empresa
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();

-- Trigger para la tabla documento
CREATE TRIGGER trigger_auditoria_documento
AFTER INSERT OR UPDATE OR DELETE ON documento
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();

-- Trigger para la tabla factura
CREATE TRIGGER trigger_auditoria_factura
AFTER INSERT OR UPDATE OR DELETE ON factura
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria();
