FROM python:3.12

WORKDIR /martInventoryService

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry 

COPY . /martInventoryService/

RUN poetry config virtualenvs.create false

RUN poetry install

EXPOSE 8006

CMD ["poetry", "run", "uvicorn", "martInventoryService.main:app", "--host", "0.0.0.0", "--port","8006", "--reload"]