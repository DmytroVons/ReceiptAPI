from fastapi import FastAPI
from .auth.routes import router as auth_router
from .receipts.routes import router as receipts_router

app = FastAPI(title="Receipt API")
app.include_router(auth_router)
app.include_router(receipts_router)

@app.get("/")
def root():
    return {"message": "Receipt API is running."}
