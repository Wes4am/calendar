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

    # Prepare the payload
    payload = {
        "firstname": request_data.get("firstname", ""),
        "lastname": request_data.get("lastname", ""),
        "phone": request_data.get("phone", ""),
        "zip": request_data.get("zip", ""),
        "apptdate": request_data.get("apptdate", ""),
        "appttime": request_data.get("appttime", ""),
        "recdDate": request_data.get("recdDate", ""),
        "recdTime": request_data.get("recdTime", ""),
        "notes": request_data.get("notes", "string"),
        "crossStreet": request_data.get("crossStreet", "string"),
        "waiver": request_data.get("waiver", "false"),
        "phone2": request_data.get("phone2", "string"),
        "phone3": request_data.get("phone3", "string"),
        "user1": request_data.get("user1", "string"),
        "user2": request_data.get("user2", "string"),
        "user3": request_data.get("user3", "string"),
        "user4": request_data.get("user4", "string"),
        "user5": request_data.get("user5", "string"),
        "rnk_id": request_data.get("rnk_id", "0"),
        "datereceived": request_data.get("datereceived", ""),
        "state": request_data.get("state", ""),
        # Add all remaining fields here
    }

    # Encode the payload for x-www-form-urlencoded
    encoded_payload = urllib.parse.urlencode(payload)

    url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(url, headers=headers, data=encoded_payload)
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
