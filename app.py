import os
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, make_response
import requests

# Configuration (change via environment variables if you want)
CATFACT_URL = os.getenv("CATFACT_URL", "https://catfact.ninja/fact")
CATFACT_TIMEOUT = float(os.getenv("CATFACT_TIMEOUT", "5"))  # seconds
USER_EMAIL = os.getenv("USER_EMAIL", "udohemmanuel2025@gmail.com")
USER_NAME = os.getenv("USER_NAME", "Emmanuel Udoh")
USER_STACK = os.getenv("USER_STACK", "Python/Flask")  # you're using Python/Flask
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")

# Logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def utc_now_iso8601_ms():
    now = datetime.now(timezone.utc)
    return now.isoformat(timespec="milliseconds").replace("+00:00", "Z")

def fetch_cat_fact():
    try:
        resp = requests.get(CATFACT_URL, timeout=CATFACT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data.get("fact"):
            return data["fact"]
        logger.warning("Cat facts API returned unexpected JSON: %s", data)
    except Exception as e:
        logger.warning("Failed to fetch cat fact: %s", e, exc_info=True)

    return "Cat fact currently unavailable. Try again soon."

@app.route("/me", methods=["GET"])
def me():
    payload = {
        "status": "success",
        "user": {
            "email": USER_EMAIL,
            "name": USER_NAME,
            "stack": USER_STACK
        },
        "timestamp": utc_now_iso8601_ms(),
        "fact": fetch_cat_fact()
    }
    return make_response(jsonify(payload), 200)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Profile API running. Open /me",
        "routes": [str(r) for r in app.url_map.iter_rules()]
    })

if __name__ == "__main__":
    logger.info("Starting app on port %s (debug=%s)", PORT, DEBUG)
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
