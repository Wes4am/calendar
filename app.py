from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to fetch the access token
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
            access_token = response.json().get("access_token")
            print(f"Fetched Access Token: {access_token}")  # Debug log
            return access_token
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
    access_token = request_data.get("access_token")  # Get token from request
    if not access_token:
        return jsonify({"error": "Access token is missing"}), 400

    required_fields = ["firstname", "lastname", "apptdate", "appttime"]
    for field in required_fields:
        if not request_data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    payload = {
        "branchID": "TMP",
        "productID": "Bath",
        "firstname": request_data.get("firstname", ""),
        "lastname": request_data.get("lastname", ""),
        "apptdate": request_data.get("apptdate", ""),
        "appttime": request_data.get("appttime", ""),
        "callmorning": request_data.get("callmorning", False),
        "callafternoon": request_data.get("callafternoon", False),
        "callevening": request_data.get("callevening", False),
        "phone": request_data.get("phone", ""),
        "email": request_data.get("email", ""),
        "address": request_data.get("address", ""),
        "city": request_data.get("city", ""),
        "postal_code": request_data.get("postal_code", ""),
    }

    url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
