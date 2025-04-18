# Script de Despliegue de Base de Datos - Facturación Demo

Este script automatiza la configuración de PostgreSQL, la creación de una base de datos y la ejecución de un esquema SQL para inicializar las tablas necesarias.

---

## **Requisitos Previos**

1. **PostgreSQL**:
   - Asegúrate de que PostgreSQL esté instalado en tu sistema.
   - Si no está instalado, el script lo instalará automáticamente.

2. **Python**:
   - Python 3 debe estar instalado en tu sistema.
   - Si no está instalado, el script lo instalará automáticamente.

3. **Archivo `.env`**:
   - Crea un archivo `.env` en el directorio raíz del proyecto con las siguientes variables:
     ```env
     DB_NAME=facturacion_db
     DB_USER=postgres
     DB_HOST=localhost
     DB_PORT=5432
     DB_PASSWORD=tu_contraseña
     ```

4. **Archivo `create_schema.sql`**:
   - Asegúrate de que el archivo `create_schema.sql` esté en el mismo directorio que el script `deploy_database.sh`.

---

## **Pasos para Ejecutar el Script**

1. **Dar Permisos de Ejecución al Script**:
   - Asegúrate de que el script tenga permisos de ejecución:
     ```bash
     chmod +x deploy_database.sh
     ```

2. **Ejecutar el Script**:
   - Ejecuta el script para configurar PostgreSQL, crear la base de datos y ejecutar el esquema SQL:
     ```bash
     ./deploy_database.sh
     ```

3. **Resultados Esperados**:
   - El script instalará PostgreSQL y Python si no están presentes.
   - Configurará la contraseña del usuario `postgres`.
   - Creará la base de datos especificada en el archivo `.env`.
   - Ejecutará el archivo `create_schema.sql` para crear las tablas necesarias.

---

## **Cómo Verificar si la Base de Datos Existe**

1. **Conéctate a PostgreSQL**:
   - Usa el siguiente comando para conectarte a PostgreSQL:
     ```bash
     PGPASSWORD="tu_contraseña" psql -U postgres -h localhost -p 5432
     ```

2. **Lista las Bases de Datos**:
   - Una vez dentro de la consola de PostgreSQL, ejecuta:
     ```sql
     \l
     ```
   - Busca el nombre de la base de datos (por ejemplo, `facturacion_db`) en la lista.

3. **Lista las Tablas de la Base de Datos**:
   - Conéctate a la base de datos:
     ```sql
     \c facturacion_db
     ```
   - Lista las tablas:
     ```sql
     \dt
     ```

4. **Verifica la Estructura de una Tabla**:
   - Por ejemplo, para la tabla `empresa`:
     ```sql
     \d empresa
     ```

5. **Salir de la Consola de PostgreSQL**:
   - Usa el comando:
     ```sql
     \q
     ```

---

## **Notas Adicionales**

- Si necesitas eliminar la base de datos para volver a intentarlo, usa el siguiente comando:
  ```bash
  PGPASSWORD="tu_contraseña" dropdb -U postgres -h localhost -p 5432 facturacion_db