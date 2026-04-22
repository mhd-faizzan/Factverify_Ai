import requests
from config.settings import get_firebase_config

_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"

# errors that hint at whether an email exists — we hide these from the user
_VAGUE_ERRORS = {"EMAIL_NOT_FOUND", "INVALID_PASSWORD", "USER_DISABLED", "INVALID_LOGIN_CREDENTIALS"}


def _url(endpoint: str) -> str:
    # URL is built fresh each call so the API key never sits in a module-level string
    key = get_firebase_config()["apiKey"]
    return f"{_BASE}:{endpoint}?key={key}"


def _generic_auth_error(raw: str) -> str:
    # never tell the user which part was wrong (email vs password)
    if any(e in raw for e in _VAGUE_ERRORS):
        return "Invalid email or password."
    if "EMAIL_EXISTS" in raw:
        return "An account with this email already exists."
    if "WEAK_PASSWORD" in raw:
        return "Password must be at least 6 characters."
    if "INVALID_EMAIL" in raw:
        return "Please enter a valid email address."
    return "Something went wrong. Please try again."


def handle_signup(first_name: str, last_name: str, email: str, password: str):
    try:
        res = requests.post(
            _url("signUp"),
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        if res.status_code != 200:
            raw = res.json().get("error", {}).get("message", "")
            return False, _generic_auth_error(raw), None

        id_token = res.json().get("idToken", "")
        requests.post(
            _url("update"),
            json={"idToken": id_token, "displayName": f"{first_name} {last_name}", "returnSecureToken": True},
            timeout=10,
        )
        return True, "Account created!", {"idToken": id_token, "first_name": first_name, "last_name": last_name}

    except requests.exceptions.Timeout:
        return False, "Request timed out. Check your connection.", None
    except requests.exceptions.ConnectionError:
        return False, "Could not connect. Check your internet.", None
    except Exception as e:
        return False, "Unexpected error. Please try again.", None


def handle_login(email: str, password: str):
    try:
        res = requests.post(
            _url("signInWithPassword"),
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10,
        )
        if res.status_code != 200:
            raw = res.json().get("error", {}).get("message", "")
            return False, _generic_auth_error(raw), None

        id_token = res.json().get("idToken", "")
        user_info = requests.post(_url("lookup"), json={"idToken": id_token}, timeout=10)
        user = user_info.json().get("users", [{}])[0]
        names = user.get("displayName", "").split() if user.get("displayName") else []

        return True, "Login successful!", {
            "idToken": id_token,
            "first_name": names[0] if names else "",
            "last_name": names[-1] if len(names) > 1 else "",
        }

    except requests.exceptions.Timeout:
        return False, "Request timed out. Check your connection.", None
    except requests.exceptions.ConnectionError:
        return False, "Could not connect. Check your internet.", None
    except Exception:
        return False, "Unexpected error. Please try again.", None
