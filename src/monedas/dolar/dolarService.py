from sqlalchemy.orm import Session
from src.monedas.dolar.dolarModel import Dolar
from src.utils.custom_request import obtener_precio_bcv
from datetime import datetime


def actualizar_dolar_unico(db: Session):
    try:
        # Iniciar una transacción explícita
        db.begin()

        # Obtener el precio del BCV y la fecha de actualización
        precio_bcv = obtener_precio_bcv()
        if not precio_bcv:
            db.rollback()  # Rollback explícito en caso de error
            return {"error": "No se pudo obtener el precio del BCV."}

        # Verificar si ya existe un registro único
        registro_existente = db.query(Dolar).first()

        if registro_existente:
            # Actualizar el registro existente
            registro_existente.precio = precio_bcv
            registro_existente.fecha_actualizacion = datetime.now()
            db.add(registro_existente)
        else:
            # Crear un nuevo registro si no existe
            nuevo_dolar = Dolar(
                fecha=datetime.today().date(),
                precio=precio_bcv,
                fecha_actualizacion=datetime.now(),
            )
            db.add(nuevo_dolar)

        # Confirmar la transacción
        db.commit()

        # Refrescar el registro actualizado o creado
        return registro_existente if registro_existente else nuevo_dolar
    except Exception as e:
        db.rollback()  # Rollback explícito en caso de excepción
        return {
            "error": f"Ocurrió un error al actualizar o crear el registro: {str(e)}"
        }


def obtener_dolar_bcv(db: Session):
    try:
        # Consultar el registro único del dólar
        registro = db.query(Dolar).first()
        if not registro:
            # Retornar un diccionario con un mensaje claro
            return {"error": "No se encontró un registro de dólar."}
        # Retornar el registro directamente si existe
        return registro.precio
    except Exception as e:
        # Registrar el error para facilitar la depuración
        return {"error": f"Ocurrió un error al obtener el registro: {str(e)}"}
