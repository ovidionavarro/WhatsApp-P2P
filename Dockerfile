FROM python:3.12-slim
WORKDIR /app
COPY chord_node.py .
COPY chord_node_reference.py .
COPY utils.py .
COPY codes.py .
EXPOSE 8001
CMD ["python","chord_node.py", "172.17.0.2"]