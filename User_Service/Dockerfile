FROM python:3.12

WORKDIR /martUserServices

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry 

COPY . /martUserServices/

RUN poetry config virtualenvs.create false

RUN poetry install

EXPOSE 8003

CMD ["poetry", "run", "uvicorn", "martUserServices.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]