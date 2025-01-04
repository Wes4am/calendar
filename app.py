from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Root route to test if the API is running
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running successfully!"})

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
            return response.json().get("access_token")
        else:
            print(f"Failed to fetch token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

# Handle preflight OPTIONS requests
@app.route("/<path:path>", methods=["OPTIONS"])
def handle_preflight(path):
    response = jsonify({"message": "Preflight request handled"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"]
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response, 204

# Endpoint 1: Submit Survey and Create Calendar
@app.route("/submit-form", methods=["POST"])
def submit_form():
    request_data = request.json
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    payload = {
        "branchid": request_data.get("branchid", "TMP"),  # Default to "TMP"
        "productid": request_data.get("productid", "Bath"),  # Default to "Bath"
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

# Endpoint 2: Book Appointment
@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    request_data = request.json
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    time_of_day = request_data.get("time_of_day", "").lower()
    call_morning = time_of_day == "morning"
    call_afternoon = time_of_day == "afternoon"
    call_evening = time_of_day == "evening"

    payload = {
        "branchID": "TMP",
        "productID": "Bath",
        "firstname": request_data.get("firstname", ""),
        "lastname": request_data.get("lastname", ""),
        "apptdate": request_data.get("apptdate", ""),
        "appttime": request_data.get("appttime", ""),
        "callmorning": call_morning,
        "callafternoon": call_afternoon,
        "callevening": call_evening,
        "phone": request_data.get("phone", ""),
        "email": request_data.get("email", ""),
        "address": request_data.get("address", ""),
        "city": request_data.get("city", ""),
        "postal_code": request_data.get("postal_code", ""),
    }

    url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
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
    app.run(host="0.0.0.0", port=5000)
