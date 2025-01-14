from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="Payment Service",
    description="Processes payments and manages transaction records.",
    version="0.1",
    root_path="/payment"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.get("/", tags=["Root"])
async def get_root():
    return {"service6": "Payment Service"}

@app.get("/process", tags=["Payment"])
async def process_payment(token: str = Depends(oauth2_scheme)):
    return {"message": "Payment processed successfully"}