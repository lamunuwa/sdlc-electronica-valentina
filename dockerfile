FROM python:3.12-slim

WORKDIR /app

# Instalacion de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación al contenedor
COPY . .

# Dar permisos de ejecución al script de arranque
RUN chmod +x start.sh

# Crear un usuario no root (sin privilegios)
RUN adduser --disabled-password --gecos "" appuser

# Cambiar la propiedad de los archivos al usuario no root
RUN chown -R appuser:appuser /app

# Elegimos a ese usuario
USER appuser

EXPOSE 8000

CMD ["bash", "start.sh"]