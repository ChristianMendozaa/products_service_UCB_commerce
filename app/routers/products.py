# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from typing import Optional

from app.deps.auth import get_current_user_either
from app.deps.permissions import can_manage_career_or_403, visible_careers_for
from app.schemas.products import ProductCreate, ProductUpdate, ProductOut, ProductList
from app.repositories import products_repo as repo
from app.services.images import upload_image_and_get_url  # ✅

router = APIRouter(prefix="/api/products", tags=["products"])

# --- RUTA PÚBLICA (antes de rutas privadas) ---
@router.get("/public", response_model=ProductList, tags=["public"])
def list_public_products(
    q: Optional[str] = Query(None, description="Búsqueda simple en nombre/descripcion"),
    category: Optional[str] = Query(None),
    career: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None, description="ISO datetime para paginación"),
):
    items, next_cursor = repo.list_products(
        q=q, category=category, career=career, limit=limit, cursor_iso=cursor, restrict_to_careers=None
    )
    return {"items": items, "next_cursor": next_cursor}

# --- LISTA AUTENTICADA ---
@router.get("", response_model=ProductList, tags=["private"])
def list_products(
    q: Optional[str] = Query(None, description="Búsqueda simple en nombre/descripcion"),
    category: Optional[str] = Query(None),
    career: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None, description="ISO datetime para paginación"),
    user=Depends(get_current_user_either),
):
    restrict_to = visible_careers_for(user["uid"])
    items, next_cursor = repo.list_products(
        q=q, category=category, career=career, limit=limit, cursor_iso=cursor,
        restrict_to_careers=restrict_to if career is None else None,
    )
    return {"items": items, "next_cursor": next_cursor}

# --- DETALLE PÚBLICO ---
@router.get("/{prod_id}", response_model=ProductOut, tags=["public"])
def get_product(prod_id: str):
    p = repo.get_product(prod_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return p

# --- CREAR JSON ---
@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED, tags=["private"])
def create_product(payload: ProductCreate, user=Depends(get_current_user_either)):
    can_manage_career_or_403(user["uid"], payload.career)
    created = repo.create_product(payload.dict(), uid=user["uid"])
    return created

# --- CREAR con FORM-DATA + archivo ---
@router.post("/form", response_model=ProductOut, status_code=status.HTTP_201_CREATED, tags=["private"])
async def create_product_form(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    career: str = Form(...),
    stock: int = Form(0),
    description: Optional[str] = Form(""),
    image_url: Optional[str] = Form(None),
    convert_webp: bool = Form(True),
    image_file: Optional[UploadFile] = File(None),
    user=Depends(get_current_user_either),
):
    can_manage_career_or_403(user["uid"], career)

    final_image = image_url or ""
    if image_file is not None:
        final_image = await upload_image_and_get_url(image_file, convert_webp=convert_webp)

    payload = {
        "name": name,
        "description": description or "",
        "price": price,
        "category": category,
        "career": career,
        "stock": stock,
        "image": final_image,
    }
    created = repo.create_product(payload, uid=user["uid"])
    return created

# --- ACTUALIZAR JSON ---
@router.put("/{prod_id}", response_model=ProductOut, tags=["private"])
def update_product(prod_id: str, payload: ProductUpdate, user=Depends(get_current_user_either)):
    current = repo.get_product(prod_id)
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    target_career = payload.career or current["career"]
    can_manage_career_or_403(user["uid"], target_career)
    updated = repo.update_product(prod_id, payload.dict(exclude_unset=True))
    assert updated is not None
    return updated

# --- ACTUALIZAR con FORM-DATA + archivo ---
@router.put("/{prod_id}/form", response_model=ProductOut, tags=["private"])
async def update_product_form(
    prod_id: str,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    career: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    convert_webp: bool = Form(True),
    image_file: Optional[UploadFile] = File(None),
    user=Depends(get_current_user_either),
):
    current = repo.get_product(prod_id)
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    target_career = career or current["career"]
    can_manage_career_or_403(user["uid"], target_career)

    final_image = image_url
    if image_file is not None:
        final_image = await upload_image_and_get_url(image_file, convert_webp=convert_webp)

    update_payload = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "career": career,
        "stock": stock,
        **({"image": final_image} if final_image is not None else {}),
    }

    updated = repo.update_product(prod_id, update_payload)
    assert updated is not None
    return updated

# --- ELIMINAR ---
@router.delete("/{prod_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["private"])
def delete_product(prod_id: str, user=Depends(get_current_user_either)):
    current = repo.get_product(prod_id)
    if not current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    can_manage_career_or_403(user["uid"], current["career"])
    ok = repo.delete_product(prod_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return
