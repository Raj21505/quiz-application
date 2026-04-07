import requests


FIREBASE_BASE = "https://identitytoolkit.googleapis.com/v1"


def _parse_error(response: requests.Response) -> str:
    try:
        err = response.json().get("error", {})
        return err.get("message", response.text)
    except Exception:
        return response.text


def sign_up(email: str, password: str, api_key: str):
    url = f"{FIREBASE_BASE}/accounts:signUp?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)

    if response.status_code == 200:
        return True, response.json(), ""

    return False, {}, _parse_error(response)


def sign_in(email: str, password: str, api_key: str):
    url = f"{FIREBASE_BASE}/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload, timeout=10)

    if response.status_code == 200:
        return True, response.json(), ""

    return False, {}, _parse_error(response)
