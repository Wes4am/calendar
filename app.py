from flask import Flask, jsonify, request
import requests
import os
from flask_cors import CORS



# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

# Function to fetch a new access token
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
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Failed to fetch token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

# Submit form endpoint
@app.route("/submit-form", methods=["POST"])
def submit_form():
    access_token = fetch_token()  # Always fetch a new token
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    request_data = request.json
    payload = {
        "branchid": request_data.get("branchid", "TMP"),
        "productid": request_data.get("productid", "Bath"),
        "zip": request_data.get("zip", ""),
    }

    url = "https://apitest.leadperfection.com/api/Leads/GetLeadsForwardLook"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
