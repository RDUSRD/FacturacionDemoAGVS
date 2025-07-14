from apscheduler.schedulers.background import BackgroundScheduler
from src.monedas.dolar.dolarService import actualizar_dolar_unico
from database import SessionLocal


def actualizar_dolar_job():
    """Función que se ejecutará en el cron job para actualizar el dólar."""
    db = SessionLocal()
    try:
        resultado = actualizar_dolar_unico(db)
        if isinstance(resultado, dict) and "error" in resultado:
            # Manejar el caso de error
            print(f"Error al actualizar el dólar: {resultado['error']}")
        else:
            # Manejar el caso exitoso
            print(f"Dólar actualizado: {resultado}")
    finally:
        db.close()


# Crear una instancia global del scheduler
scheduler = BackgroundScheduler()


def iniciar_cron_job():
    """Configura y arranca el cron job."""
    # Evitar agregar múltiples trabajos si el scheduler ya está en ejecución
    if not scheduler.running:
        # Ejecutar cada 12 horas
        scheduler.add_job(actualizar_dolar_job, "interval", hours=12)
        scheduler.start()
        print("Cron job para actualizar el dólar configurado.")

    # Ejecutar la tarea inmediatamente al iniciar
    actualizar_dolar_job()
    print("Tarea de actualización del dólar ejecutada al inicio.")


def detener_cron_job():
    """Detiene el cron job."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("Cron job para actualizar el dólar detenido.")
