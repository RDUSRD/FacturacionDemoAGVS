# Usa una imagen base de Python más reciente
FROM python:3.11-slim

# Instala herramientas básicas y dependencias del sistema
RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    libgirepository-1.0-1 \
    gir1.2-glib-2.0 \
    libglib2.0-dev \
    libpango-1.0-0 \
    libcairo2 \
    libffi-dev \
    libjpeg62-turbo-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Asegúrate de copiar el script wait-for-it.sh
COPY wait-for-it.sh /app/wait-for-it.sh

# Haz que el script sea ejecutable
RUN chmod +x /app/wait-for-it.sh

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]