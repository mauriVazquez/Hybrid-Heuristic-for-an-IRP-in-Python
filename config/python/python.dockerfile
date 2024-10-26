FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

# Instala dependencias del sistema necesarias para compilar numpy
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --upgrade -r requirements.txt \
    && apk del .build-deps  # Elimina las dependencias de compilación

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
