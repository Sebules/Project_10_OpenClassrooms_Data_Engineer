FROM python:3.13-slim
RUN pip install --upgrade pip
RUN pip install --no-cache-dir duckdb kestra pandas pytest