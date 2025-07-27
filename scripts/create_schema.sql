-- Este script crea las tablas necesarias para la base de datos de facturación
-- de acuerdo a la estructura definida en el modelo de datos.

-- Comando para ejecutar el script:
-- psql -U <usuario> -d <nombre_base_datos> -f create_schema.sql

-- Comando para verificar la creación de las tablas:
-- \dt

-- Crear tabla EMPRESA
CREATE TABLE IF NOT EXISTS empresa (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rif VARCHAR(50) NOT NULL UNIQUE,
    domicilio_fiscal TEXT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255)
);

-- Crear tabla CLIENTE
CREATE TABLE IF NOT EXISTS cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rif VARCHAR(50) NOT NULL UNIQUE,
    domicilio_fiscal TEXT NOT NULL
);

-- Crear tabla DOCUMENTO
CREATE TABLE IF NOT EXISTS documento (
    id SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(50) NOT NULL,
    numero_control VARCHAR(50) NOT NULL UNIQUE,
    fecha_emision DATE NOT NULL,
    hora_emision TIME NOT NULL,
    empresa_id INT NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    cliente_id INT NOT NULL REFERENCES cliente(id) ON DELETE CASCADE,
    estado VARCHAR(50) NOT NULL
);

-- Crear tabla FACTURA
CREATE TABLE IF NOT EXISTS factura (
    id SERIAL PRIMARY KEY,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    documento_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE
);

-- Crear tabla PRODUCTO
CREATE TABLE IF NOT EXISTS producto (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'activo',
    stock INT NOT NULL DEFAULT 0,
    codigo_barras VARCHAR(100) UNIQUE,
    codigo_QR VARCHAR(100) UNIQUE,
    exento BOOLEAN DEFAULT FALSE,
    descuento DECIMAL(10, 2) DEFAULT 0.0
);

-- Crear tabla DETALLE_FACTURA
CREATE TABLE IF NOT EXISTS detalle_factura (
    id SERIAL PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL REFERENCES producto(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla NOTA_DEBITO
CREATE TABLE IF NOT EXISTS nota_debito (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla NOTA_CREDITO
CREATE TABLE IF NOT EXISTS nota_credito (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla ORDEN_ENTREGA
CREATE TABLE IF NOT EXISTS orden_entrega (
    id SERIAL PRIMARY KEY,
    bienes_entregados JSON NOT NULL,
    documento_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE
);

-- Crear tabla COMPROBANTE_RETENCION
CREATE TABLE IF NOT EXISTS comprobante_retencion (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    tipo_impuesto VARCHAR(50) NOT NULL,
    monto_retenido DECIMAL(10, 2) NOT NULL
);

-- Crear tabla AUDITORIA
CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(255) NOT NULL,
    registro_id INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(255) NOT NULL
);

-- Crear tabla PEDIDO
CREATE TABLE IF NOT EXISTS pedido (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES cliente(id) ON DELETE CASCADE,
    empresa_id INT NOT NULL REFERENCES empresa(id) ON DELETE CASCADE,
    estado VARCHAR(50) DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '2 hours',
    total DECIMAL(10, 2),
    observaciones VARCHAR(255)
);

-- Crear tabla DETALLE_PEDIDO
CREATE TABLE IF NOT EXISTS detalle_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INT NOT NULL REFERENCES pedido(id) ON DELETE CASCADE,
    producto_id INT NOT NULL REFERENCES producto(id) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    descuento DECIMAL(10, 2) DEFAULT 0.0,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla DOLAR
CREATE TABLE IF NOT EXISTS dolar (
    id SERIAL PRIMARY KEY,
    fecha DATE DEFAULT CURRENT_DATE NOT NULL,
    precio FLOAT NOT NULL,
    fecha_actualizacion TIMESTAMP NOT NULL
);