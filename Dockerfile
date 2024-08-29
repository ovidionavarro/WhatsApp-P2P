FROM python:3.12-slim
WORKDIR /app
COPY chord_node.py .
CMD ["python","chord_node.py"]