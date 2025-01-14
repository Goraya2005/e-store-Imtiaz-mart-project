from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlmodel import Session
from martOrderService.service import *
from martOrderService.db import create_db_and_tables, db_session
from typing import Annotated
from aiokafka import AIOKafkaProducer

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database connection")
    create_db_and_tables()
    yield

app = FastAPI(
    title="Order Service",
    description="Handles order creation, updating, and tracking",
    version="0.1",
    lifespan=lifespan,
    root_path="/order"
)

@app.get("/" ,tags=["Root"])
async def get_root():
    return {"service":"Order Service"}

@app.get("/getorders", tags=["Order"] ,response_model=list[Order])
def get_order(db: Annotated[Session, Depends(db_session)],user = Depends(get_current_user)):
    order = service_get_order(db,user)
    return order

@app.get("/getorder/{order_id}",response_model=Order)
async def get_order_by_id(order_id:int,db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    order = service_get_order_by_id(db,order_id,user)
    return order

@app.get("/getdeliveredorders",tags=["Order"],response_model=list[Order])
async def get_delivered_orders(db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    deivered_order = service_get_delivered_orders(db)
    return deivered_order

@app.get("/getpaidorders",tags=["Order"],response_model=list[Order])
async def get_delivered_orders(db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    paid_order = service_get_paid_orders(db)
    return paid_order


@app.get("/getpendingorders",tags=["Order"],response_model=list[Order])
async def get_delivered_orders(db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    pending_order = service_get_pending_orders(db)
    return pending_order

@app.post("/createorder", response_model=OrderRead, tags=["Order"])
async def create_order(order_data:OrderCreate, session:Annotated[Session, Depends(db_session)],user: Annotated[User, Depends(get_current_user)], producer: Annotated[AIOKafkaProducer, Depends(produce_message)]) -> OrderRead:
    
    order_info = Order.model_validate(order_data)
    order = await service_create_order(session, order_info,user, producer)
    return order

@app.patch("/updateorder", tags=["Order"])
async def update_order(order_update:OrderUpdate,order_id,session:Annotated[Session, Depends(db_session)], user = Depends(get_current_user)):
    order = service_get_order_by_id(session,order_id,user)
    if order:
        order_data = order_update.model_dump(exclude_unset = True)
        order.sqlmodel_update(order_data)
        session.add(order)
        session.commit()
        session.refresh(order)
        if order_update.order_status == "cancelled" or order_update.order_status == "delivered" or order_update.order_status == "paid":
            return service_order_update(session,user,order_id)
        return order 

@app.delete("/deleteorder", tags=["Order"])
async def delete_order(order_id, user:Annotated[User, Depends(get_current_user)], session:Annotated[Session, Depends(db_session)]):
    deleted_order = service_delete_order(session,order_id,user)
    return deleted_order

@app.post("/addtocart", response_model=CartRead, tags=["Cart"])
async def add_to_cart(product_id:int,cart_info:CartCreate,session:Annotated[Session,Depends(db_session)],user:Annotated[User, Depends(get_current_user)]):
    cart_data = Cart.model_validate(cart_info)
    cart = service_add_to_cart(session,cart_data,user,product_id)
    return cart

@app.get("/getcarts",response_model=list[Cart],tags=["Cart"])
async def get_cart(db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    carts = db.exec(select(Cart).where(Cart.user_id == user.id)).all()
    if carts is None:
        raise HTTPException(status_code=200,detail="Cart is empty!")
    return carts

@app.get("/getproductfromcart", response_model=list[ProductRead], tags=["Cart"])
async def get_product_from_cart(session:Annotated[Session,Depends(db_session)],user:Annotated[User, Depends(get_current_user)]):
    return service_get_product_from_cart(session,user)

@app.delete("/removecart/{cart_id}",tags=["Cart"])
async def remove_cart_by_id(cart_id:int,db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    service_remove_cart_by_id(db,user,cart_id)
    return {"message":"Cart is removed"}

@app.patch("/updatecart/add",response_model=CartRead,tags=["Cart"])
async def update_cart_add(cart_id:int,product_id:int,db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    service_update_cart_add(db,cart_id,user,product_id)
    return service_get_cart_by_id(db,cart_id,user)
    

@app.patch("/updatecart/minus",response_model=CartRead,tags=["Cart"])
async def update_cart_minus(cart_id:int,product_id:int,db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    service_update_cart_minus(db,cart_id,user,product_id)
    return service_get_cart_by_id(db,cart_id,user)


@app.delete("/removecart",tags=["Cart"])
async def remove_cart(db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    service_remove_cart(db,user)
    return {"message":"remove all carts"}

@app.get("/getorderitem",tags=["Orderitem"])
async def get_order_item(order_id:int,db:Session = Depends(db_session),user:User = Depends(get_current_user)):
    orderitem = service_get_order_item(db,order_id,user)
    return orderitem