from flask import Flask, jsonify
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Global variable to store the token
token_data = {"token": None}

# Function to fetch the token
def fetch_token():
    url = "https://apitest.leadperfection.com/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type": "password",
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "clientid": os.getenv("CLIENTID"),
        "appkey": os.getenv("APPKEY"),
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            token_data["token"] = response.json()
            print("Token updated successfully!")
        else:
            print(f"Failed to fetch token: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching token: {e}")

# Schedule the token refresh every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_token, "interval", hours=24)
scheduler.start()

# API route to get the token
@app.route("/get-token", methods=["GET"])
def get_token():
    if token_data["token"]:
        return jsonify(token_data["token"])
    else:
        return jsonify({"error": "Token not available yet"}), 500

# Run the initial token fetch when the server starts
fetch_token()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
