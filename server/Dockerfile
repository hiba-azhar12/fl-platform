FROM python:3.10-slim
WORKDIR /app
RUN pip install flwr==1.5.0 --quiet
COPY server.py .
CMD ["python", "server.py"]
