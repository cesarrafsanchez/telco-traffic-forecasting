# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero los requerimientos para aprovechar la caché de capas de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente y el modelo
# Ajusta las rutas según tu estructura final
COPY src/ ./src/


# Exponemos el puerto que usa FastAPI (8000)
EXPOSE 8000

# Comando para iniciar la aplicación
# Usamos uvicorn para levantar FastAPI
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]