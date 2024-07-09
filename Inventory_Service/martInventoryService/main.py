from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import Session
from fastapi import FastAPI
from myService.models import *
from myService.service import *
from myService.database import *

app = FastAPI(
    title="Inventory Service",
    description="Manages stock levels and inventory updates",
    version="1.0",
    lifespan=lifespan,
    root_path="/inventory"
)

@app.get("/")
async def main():
    return {"service":"Inventory service"}


@app.get("/get-inventory")
async def get_inventory(db:Annotated[Session,Depends(db_session)]):
    invetory = service_get_inventory(db)
    return invetory

@app.post("/create-inventory")
async def create_inventory(db:Annotated[Session,Depends(db_session)],inventory_data:InventoryCreate):
    inventory = service_create_inventory(db,inventory_data)
    return inventory