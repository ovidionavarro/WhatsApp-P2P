FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY chord_node.py .
COPY chord_node_reference.py .
COPY utils.py .
COPY codes.py .
COPY view.py .
COPY db.py .
# Copiar las plantillas HTML y archivos estáticos
COPY templates/ templates/
COPY static/ static/

# Instalar Flask
RUN pip install flask

# Exponer el puerto 8001
EXPOSE 5001

# Comando para ejecutar la aplicación Flask
CMD ["python", "view.py"]