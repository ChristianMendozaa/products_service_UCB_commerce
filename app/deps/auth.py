# app/deps/auth.py
from fastapi import Header, HTTPException, status, Request
from firebase_admin import auth as fb_auth
from typing import Optional
from app.config import ENABLE_FIRESTORE_PROVISIONING, SESSION_COOKIE_NAME
from app.core.firebase import firestore_db
import logging

logger = logging.getLogger(__name__)

SKEW_SECONDS = 15  # tolerancia de reloj para "Token used too early"

def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

def _verify_session_with_skew(cookie: str):
    try:
        return fb_auth.verify_session_cookie(cookie, check_revoked=False)
    except Exception as e:
        if "Token used too early" in str(e):
            logger.warning("verify_session_cookie: early, retry with %ss", SKEW_SECONDS)
            return fb_auth.verify_session_cookie(
                cookie,
                check_revoked=False,
                clock_skew_seconds=SKEW_SECONDS,
            )
        raise

def _verify_id_token_with_skew(token: str):
    try:
        return fb_auth.verify_id_token(token)
    except Exception as e:
        if "Token used too early" in str(e):
            logger.warning("verify_id_token: early, retry with %ss", SKEW_SECONDS)
            return fb_auth.verify_id_token(token, clock_skew_seconds=SKEW_SECONDS)
        raise

async def get_current_user_either(request: Request, authorization: Optional[str] = Header(None)):
    """
    Autenticación híbrida:
    1) Intenta Authorization: Bearer <id_token>
    2) Fallback a cookie de sesión (SESSION_COOKIE_NAME)
    """
    # 1) Bearer primero (más robusto entre dominios)
    token = _extract_bearer(authorization)
    if token:
        try:
            decoded = _verify_id_token_with_skew(token)
        except Exception as e:
            logger.exception("verify_id_token failed")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")
    else:
        # 2) Cookie de sesión
        session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
        if not session_cookie:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido.")
        try:
            decoded = _verify_session_with_skew(session_cookie)
        except Exception as e:
            logger.exception("verify_session_cookie failed")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada.")

    uid = decoded.get("uid")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UID faltante.")

    profile = None
    if ENABLE_FIRESTORE_PROVISIONING:
        try:
            doc_ref = firestore_db.collection("users").document(uid)
            doc = doc_ref.get()
            if not doc.exists:
                profile = {
                    "uid": uid,
                    "email": decoded.get("email"),
                    "displayName": decoded.get("name"),
                    "photoURL": decoded.get("picture"),
                    "providers": (decoded.get("firebase") or {}).get("sign_in_provider"),
                }
                doc_ref.set(profile, merge=True)
            else:
                profile = doc.to_dict()
        except Exception:
            profile = None

    return {
        "uid": uid,
        "email": decoded.get("email"),
        "displayName": decoded.get("name"),
        "photoURL": decoded.get("picture"),
        "profile": profile,
        "firebase_claims": decoded,
    }

# Alias de compatibilidad si en otras partes importabas get_current_user
get_current_user = get_current_user_either
