FROM python:3.11-slim

WORKDIR /usr/src/app

# Instalar dependencias necesarias para compilar ortools
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make \
    && rm -rf /var/lib/apt/lists/*

# Instalar ortools
RUN pip install --upgrade pip && \
    pip install ortools

COPY ./requirements.txt /usr/src/app/requirements.txt

# Instalar dependencias adicionales
RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
