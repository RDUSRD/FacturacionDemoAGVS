#!/bin/bash

# Deployment Script para la Base de Datos de Facturación
# Este script instala las dependencias necesarias, configura PostgreSQL, ajusta la contraseña del usuario root (postgres),
# crea un usuario seguro para la aplicación y ejecuta el script SQL para crear las tablas.

# -------------------------------
# PREREQUISITOS O DEPENDENCIAS
# -------------------------------
# 1. PostgreSQL debe estar instalado en el sistema.
#    - En Ubuntu: sudo apt update && sudo apt install postgresql postgresql-contrib
# 2. Python debe estar instalado en el sistema.
#    - En Ubuntu: sudo apt update && sudo apt install python3 python3-pip
# 3. El servicio de PostgreSQL debe estar en ejecución.
#    - En Linux: sudo systemctl start postgresql
# 4. El archivo `.env` debe estar configurado en el root del proyecto con las siguientes variables:
#    - DB_NAME, DB_USER, DB_HOST, DB_PORT, DB_PASSWORD.

# -------------------------------
# CARGAR VARIABLES DE ENTORNO
# -------------------------------
if [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
else
    echo "Error: No se encontró el archivo .env en el directorio raíz del proyecto."
    exit 1
fi

# -------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------
DB_NAME=${DB_NAME:-facturacion_db}
DB_USER=${DB_USER:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}
APP_USER=${APP_USER:-"app_user"}
APP_PASSWORD=${APP_PASSWORD:-"app_password"}
SQL_SCRIPT="create_schema.sql"

# -------------------------------
# FUNCIONES AUXILIARES
# -------------------------------

# Manejo de errores
function handle_error() {
    echo "Error: $1"
    exit 1
}

# Verificar si PostgreSQL está instalado, si no, instalarlo
function install_postgresql() {
    if ! command -v psql &> /dev/null; then
        echo "PostgreSQL no está instalado. Instalándolo ahora..."
        sudo apt update || handle_error "No se pudo actualizar los paquetes."
        sudo apt install -y postgresql postgresql-contrib || handle_error "No se pudo instalar PostgreSQL."
        echo "PostgreSQL instalado exitosamente."
    else
        echo "PostgreSQL ya está instalado."
    fi
}

# Verificar si Python está instalado, si no, instalarlo
function install_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Python no está instalado. Instalándolo ahora..."
        sudo apt update || handle_error "No se pudo actualizar los paquetes."
        sudo apt install -y python3 python3-pip || handle_error "No se pudo instalar Python."
        echo "Python instalado exitosamente."
    else
        echo "Python ya está instalado."
    fi
}

# Verificar si el servicio de PostgreSQL está activo
function check_postgresql_running() {
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        echo "El servicio de PostgreSQL no está en ejecución. Iniciándolo ahora..."
        sudo systemctl start postgresql || handle_error "No se pudo iniciar el servicio de PostgreSQL."
        echo "PostgreSQL iniciado exitosamente."
    else
        echo "El servicio de PostgreSQL ya está en ejecución."
    fi
}

# Configurar la contraseña del usuario root (postgres)
function configure_postgres_password() {
    echo "Configurando la contraseña del usuario root (postgres)..."
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$DB_PASSWORD';" || handle_error "No se pudo configurar la contraseña del usuario root."
    echo "Contraseña del usuario root configurada correctamente."
}

# Crear un usuario seguro para la aplicación
function create_app_user() {
    echo "Creando un usuario seguro para la aplicación..."
    sudo -u postgres psql -c "DO \$\$ BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE ROLE $APP_USER LOGIN PASSWORD '$APP_PASSWORD';
            GRANT CONNECT ON DATABASE $DB_NAME TO $APP_USER;
            GRANT USAGE ON SCHEMA public TO $APP_USER;
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $APP_USER;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $APP_USER;
        END IF;
    END \$\$;" || handle_error "No se pudo crear el usuario seguro para la aplicación."
    echo "Usuario seguro creado correctamente."
}

# Crear la base de datos si no existe
function create_database() {
    echo "Verificando si la base de datos '$DB_NAME' existe..."
    if ! PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo "La base de datos '$DB_NAME' no existe. Creándola..."
        PGPASSWORD="$DB_PASSWORD" createdb -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME" || handle_error "No se pudo crear la base de datos '$DB_NAME'."
        echo "Base de datos '$DB_NAME' creada exitosamente."
    else
        echo "La base de datos '$DB_NAME' ya existe. Continuando..."
    fi
}

# Ejecutar el script SQL
function execute_sql_script() {
    echo "Ejecutando el script SQL '$SQL_SCRIPT'..."
    if ! PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -f "$SQL_SCRIPT"; then
        handle_error "Error al ejecutar el script SQL. Por favor, revisa el archivo '$SQL_SCRIPT'."
    fi
    echo "El script SQL se ejecutó correctamente."
}

# -------------------------------
# EJECUCIÓN DEL SCRIPT
# -------------------------------

echo "Iniciando el Deployment Script para la Base de Datos de Facturación..."

install_postgresql
install_python
check_postgresql_running
configure_postgres_password
create_database
create_app_user
execute_sql_script

echo "Deployment completado exitosamente."