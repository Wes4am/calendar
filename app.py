from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to store the token and expiry
ACCESS_TOKEN = None
TOKEN_EXPIRY = 0  # Timestamp for when the token expires

# Function to fetch and refresh the access token
def fetch_token():
    global ACCESS_TOKEN, TOKEN_EXPIRY

    # Check if the token is still valid
    current_time = time.time()
    if ACCESS_TOKEN and current_time < TOKEN_EXPIRY:
        print("Using cached access token.")
        return ACCESS_TOKEN

    print("Fetching a new access token.")
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
            ACCESS_TOKEN = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 86400)  # Default to 24 hours
            TOKEN_EXPIRY = current_time + expires_in - 60  # Refresh 1 minute before expiry
            print(f"New Access Token: {ACCESS_TOKEN}")
            return ACCESS_TOKEN
        else:
            print(f"Failed to fetch token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

# Root route to test if the API is running
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running successfully!"})

# Endpoint 1: Submit Survey and Return Access Token
@app.route("/submit-form", methods=["POST"])
def submit_form():
    access_token = fetch_token()  # Fetch token for this request
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
            data = response.json()
            return jsonify({"data": data, "access_token": access_token})  # Include token
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: Book Appointment
@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    request_data = request.json
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    # Prepare the payload with additional fields
    payload = {
        "firstname": request_data.get("firstname"),
        "lastname": request_data.get("lastname"),
        "phone": request_data.get("phone"),
        "zip": request_data.get("zip"),
        "apptdate": request_data.get("apptdate"),   # Added field
        "appttime": request_data.get("appttime"),   # Added field
        "recdDate": request_data.get("recdDate"),   # Added field
        "recdTime": request_data.get("recdTime"),   # Added field
        "pro_id": request_data.get("pro_id"),       # Added field
    }

    # Add user1 to user15 with empty data
    for i in range(1, 16):
        payload[f"user{i}"] = ""

    url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Debugging logs
    print(f"Access Token Used: {access_token}")
    print(f"Payload Sent: {payload}")
    print(f"Headers Sent: {headers}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        print(f"Error during API call: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
