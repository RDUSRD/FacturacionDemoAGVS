"""
database.py
This module sets up the database connection using SQLAlchemy and provides utility functions for database sessions.

Dependencies:
- time: For retrying database connection.
- sqlalchemy: For ORM and database connection.
- dotenv.load_dotenv: For loading environment variables from a .env file.
- os: For accessing environment variables.

Environment Variables:
- SQLALCHEMY_DATABASE_URL: Database connection URL.

Functions:
- get_db: Yields a database session for use in FastAPI routes.
"""

import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
print(f"Conectando a la base de datos: {DATABASE_URL}")

for _ in range(10):  # Intentar 10 veces
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("Conexión exitosa a la base de datos")
        break
    except OperationalError:
        print("Base de datos no disponible, reintentando en 5 segundos...")
        time.sleep(5)
else:
    print("No se pudo conectar a la base de datos después de varios intentos")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()