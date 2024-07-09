from fastapi import FastAPI
from contextlib import asynccontextmanager
from forServices.db import create_db_and_tables  # Assuming this creates the database and tables
import asyncio
from forServices.services import user_consumer_task, order_consumer_task
from forServices import settings  # Assuming this module holds settings like email credentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from typing import List

class EmailSchema(BaseModel):
    email: List[EmailStr]  # List of email addresses for recipients

# Consider using environment variables for email credentials (more secure)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_email,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,  # Assuming these exist in settings
    MAIL_PORT=465,
    MAIL_SERVER=settings.smtp_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM=settings.smtp_email
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    create_db_and_tables()  # Call to create database and tables (if necessary)
    asyncio.create_task(user_consumer_task())
    asyncio.create_task(order_consumer_task())
    yield


app = FastAPI(
    title="Notification Service",
    description="Sends notifications (email, SMS) to users about order statuses and other updates.",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/notification"
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"Service": "Notification Service"}


@app.post("/send_mail")
async def send_mail(email: EmailSchema):
    # Personalize the email body with user information if possible
    body = f"Dear {', '.join(email.email)}, \n\n Your order has been placed successfully! \n\n Best regards, \n Team Imtiaz Mart"  # Use ', '.join() for a comma-separated list

    message = MessageSchema(
        subject="Order Confirmation",
        recipients=email.email,  # List of email addresses
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return JSONResponse(status_code=200, content={"message": "Email has been sent"})
