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

4. **Archivos SQL**:
   - Asegúrate de que los archivos `create_schema.sql` y `auditoria_triggers.sql` estén en el mismo directorio que el script `deploy_database.sh`.

---

## **Pasos para Ejecutar el Script**

1. **Dar Permisos de Ejecución al Script**:
   - Asegúrate de que el script tenga permisos de ejecución:
     ```bash
     chmod +x deploy_database.sh
     ```

2. **Ejecutar el Script**:
   - Ejecuta el script para configurar PostgreSQL, crear la base de datos y ejecutar los esquemas SQL:
     ```bash
     ./deploy_database.sh
     ```

3. **Resultados Esperados**:
   - El script instalará PostgreSQL y Python si no están presentes.
   - Configurará la contraseña del usuario `postgres`.
   - Creará la base de datos especificada en el archivo `.env`.
   - Ejecutará el archivo `create_schema.sql` para crear las tablas necesarias.
   - Ejecutará el archivo `auditoria_triggers.sql` para configurar los triggers de auditoría.

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

5. **Verifica los Triggers Configurados**:
   - Lista los triggers configurados en una tabla, por ejemplo, `empresa`:
     ```sql
     \d+ empresa
     ```

6. **Salir de la Consola de PostgreSQL**:
   - Usa el comando:
     ```sql
     \q
     ```

---

## **Notas Adicionales**

- Si necesitas eliminar la base de datos para volver a intentarlo, usa el siguiente comando:
  ```bash
  PGPASSWORD="tu_contraseña" dropdb -U postgres -h localhost -p 5432 facturacion_db
  ```

---

## **Comentarios de Expansión Futura**

1. **Soporte para múltiples entornos**:
   - Usar variables de entorno (.env) para configurar parámetros como DB_NAME, DB_USER, etc.
   - Implementar herramientas como `dotenv` para cargar configuraciones dinámicamente.

2. **Escalabilidad hacia imprenta digital**:
   - Agregar soporte para múltiples sucursales, inventarios y órdenes de impresión.
   - Mejorar el sistema de auditoría para rastrear cambios en documentos y operaciones.

3. **Separación en microservicios**:
   - Dividir servicios en módulos independientes (clientes, documentos, auditoría, etc.).
   - Usar bases de datos específicas por microservicio o una compartida.

4. **Migraciones de esquema**:
   - Usar herramientas como Alembic o Flyway para manejar cambios en la base de datos.

5. **Integración con servicios externos**:
   - Preparar la base de datos para integrarse con APIs de facturación electrónica o sistemas de pago.

6. **Optimización y monitoreo**:
   - Implementar índices adicionales y monitorear consultas con `EXPLAIN`.
   - Usar herramientas como Grafana y Prometheus para monitorear la base de datos.

7. **Seguridad y cumplimiento**:
   - Cifrar columnas sensibles y cumplir con normativas como GDPR o CCPA.

---

## **Planes de Mantenimiento**

1. **Mantenimiento Preventivo**:
   - Realizar respaldos automáticos periódicos con `pg_dump` o `pgBackRest`.
   - Monitorear el rendimiento de la base de datos y optimizar índices regularmente.
   - Revisar logs de PostgreSQL para identificar posibles problemas.

2. **Mantenimiento Correctivo**:
   - Corregir errores en el esquema o datos detectados durante las operaciones.
   - Restaurar la base de datos desde un respaldo en caso de fallos.

3. **Mantenimiento Evolutivo**:
   - Actualizar el esquema de la base de datos para soportar nuevas funcionalidades.
   - Implementar migraciones controladas con herramientas como Alembic o Flyway.

4. **Mantenimiento Predictivo**:
   - Usar herramientas de monitoreo (Grafana, Prometheus) para detectar patrones de uso.
   - Configurar alertas para identificar consultas lentas o problemas de rendimiento.