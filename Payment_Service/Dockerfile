FROM python:3.12

WORKDIR /martPaymentServices

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry 

COPY . /martPaymentServices/

RUN poetry config virtualenvs.create false

RUN poetry install

EXPOSE 8008

CMD ["poetry", "run", "uvicorn", "martPaymentServices.main:app", "--host", "0.0.0.0", "--port","8008", "--reload"]