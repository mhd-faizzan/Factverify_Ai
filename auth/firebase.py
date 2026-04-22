import requests
from config.settings import get_firebase_config

_cfg = get_firebase_config()

SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_cfg['apiKey']}"
LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={_cfg['apiKey']}"
UPDATE_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={_cfg['apiKey']}"
LOOKUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={_cfg['apiKey']}"


def handle_signup(first_name, last_name, email, password):
    try:
        res = requests.post(SIGNUP_URL, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        if res.status_code != 200:
            return False, res.json().get("error", {}).get("message", "Unknown error"), None

        id_token = res.json().get("idToken", "")
        requests.post(UPDATE_URL, json={"idToken": id_token, "displayName": f"{first_name} {last_name}", "returnSecureToken": True}, timeout=10)

        return True, "Account created!", {"idToken": id_token, "first_name": first_name, "last_name": last_name}
    except Exception as e:
        return False, f"Connection error: {e}", None


def handle_login(email, password):
    try:
        res = requests.post(LOGIN_URL, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        if res.status_code != 200:
            return False, res.json().get("error", {}).get("message", "Unknown error"), None

        id_token = res.json().get("idToken", "")
        user_info = requests.post(LOOKUP_URL, json={"idToken": id_token}, timeout=10)
        user = user_info.json().get("users", [{}])[0]
        names = user.get("displayName", "").split() if user.get("displayName") else []

        return True, "Login successful!", {
            "idToken": id_token,
            "first_name": names[0] if names else "",
            "last_name": names[-1] if len(names) > 1 else "",
        }
    except Exception as e:
        return False, f"Connection error: {e}", None
