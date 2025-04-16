-- Este script crea las tablas necesarias para la base de datos de facturación
-- de acuerdo a la estructura definida en el modelo de datos.

-- Comando para ejecutar el script:
-- psql -U <usuario> -d <nombre_base_datos> -f create_schema.sql

-- Comando para verificar la creación de las tablas:
-- \dt


-- Crear tabla EMPRESA
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rif VARCHAR(50) NOT NULL UNIQUE,
    domicilio_fiscal TEXT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255)
);

-- Crear tabla CLIENTE
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rif VARCHAR(50) NOT NULL UNIQUE,
    domicilio_fiscal TEXT NOT NULL
);

-- Crear tabla DOCUMENTO
CREATE TABLE documento (
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
CREATE TABLE factura (
    id SERIAL PRIMARY KEY,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    documento_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE
);

-- Crear tabla DETALLE_FACTURA
CREATE TABLE detalle_factura (
    id SERIAL PRIMARY KEY,
    factura_id INT NOT NULL REFERENCES factura(id) ON DELETE CASCADE,
    producto_id INT NOT NULL REFERENCES producto(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla PRODUCTO
CREATE TABLE producto (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Crear tabla NOTA_DEBITO
CREATE TABLE nota_debito (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla NOTA_CREDITO
CREATE TABLE nota_credito (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    operaciones JSON NOT NULL,
    montos_base_iva JSON NOT NULL,
    monto_exento DECIMAL(10, 2) NOT NULL,
    montos_iva JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- Crear tabla ORDEN_ENTREGA
CREATE TABLE orden_entrega (
    id SERIAL PRIMARY KEY,
    bienes_entregados JSON NOT NULL,
    documento_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE
);

-- Crear tabla COMPROBANTE_RETENCION
CREATE TABLE comprobante_retencion (
    id SERIAL PRIMARY KEY,
    documento_relacionado_id INT NOT NULL REFERENCES documento(id) ON DELETE CASCADE,
    tipo_impuesto VARCHAR(50) NOT NULL,
    monto_retenido DECIMAL(10, 2) NOT NULL
);

-- Crear tabla AUDITORIA
CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(255) NOT NULL,
    registro_id INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalles TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(255) NOT NULL
);