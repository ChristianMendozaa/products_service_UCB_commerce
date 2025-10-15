# app/main.py  (añade esto)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.products import router as products_router
from app.config import ALLOWED_ORIGINS

app = FastAPI(title="Auth + FastAPI + Firebase", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'https://ucb-e-commerce.vercel.app'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(products_router)  # ✅

@app.get("/health")
def health():
    return {"ok": True}
