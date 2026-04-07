import os
import json
from typing import Optional

import firebase_admin
from fastapi import Header, HTTPException
from firebase_admin import auth, credentials


def init_firebase() -> None:
    if firebase_admin._apps:
        return

    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "credentials.json")
    db_url = os.getenv(
        "FIREBASE_DB_URL",
        "https://quiz-app-21-default-rtdb.asia-southeast1.firebasedatabase.app/",
    )

    if cred_json:
        try:
            cred_info = json.loads(cred_json)
            cred = credentials.Certificate(cred_info)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_CREDENTIALS_JSON is not valid JSON") from exc
    else:
        if not os.path.exists(cred_path):
            raise RuntimeError(
                f"Firebase credentials file not found at '{cred_path}'. "
                "Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON correctly."
            )
        cred = credentials.Certificate(cred_path)

    options = {"databaseURL": db_url} if db_url else None

    if options:
        firebase_admin.initialize_app(cred, options)
    else:
        firebase_admin.initialize_app(cred)


def verify_firebase_token(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {exc}")
