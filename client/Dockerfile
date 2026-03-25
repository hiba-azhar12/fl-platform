FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*
RUN pip install flwr==1.5.0 lightgbm pandas pyarrow scikit-learn tenseal --quiet
COPY . .
CMD ["python", "client.py"]