from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@app.route("/")
def home():
    return "License Server Running"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json

    key = data.get("key")
    hwid = data.get("hwid")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{key}",
        headers=headers
    )

    rows = r.json()

    if not rows:
        return jsonify({"status": "invalid"})

    row = rows[0]

    if row["hwid"] is None:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/licenses?license_key=eq.{key}",
            headers={**headers, "Content-Type": "application/json"},
            json={"hwid": hwid}
        )
        return jsonify({"status": "activated"})

    if row["hwid"] == hwid:
        return jsonify({"status": "valid"})

    return jsonify({"status": "used_on_another_device"})

if __name__ == "__main__":
    app.run()
