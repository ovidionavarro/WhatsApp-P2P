FROM python:3.12-slim
WORKDIR /app
COPY chord_node.py .
COPY chord_node_reference.py .
COPY codes.py .
COPY utils.py .
CMD ["python","chord_node.py"]