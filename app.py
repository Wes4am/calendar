from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Automatically handle CORS for all routes

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

# Endpoint 1: Submit Survey and Create Calendar
@app.route("/submit-survey", methods=["POST"])
def submit_survey():
    survey_data = request.json
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    survey_payload = {
        "branchid": "TMP",
        "productid": "Bath",
        "zip": survey_data.get("postal_code", ""),
    }

    survey_url = "https://apitest.leadperfection.com/api/Leads/GetLeadsForwardLook"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(survey_url, headers=headers, data=survey_payload)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: Book Appointment
@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    appointment_data = request.json
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    time_of_day = appointment_data.get("time_of_day", "").lower()
    call_morning = time_of_day == "morning"
    call_afternoon = time_of_day == "afternoon"
    call_evening = time_of_day == "evening"

    booking_payload = {
        "branchID": "TMP",
        "productID": "Bath",
        "firstname": appointment_data.get("firstname", ""),
        "lastname": appointment_data.get("lastname", ""),
        "apptdate": appointment_data.get("apptdate", ""),
        "appttime": appointment_data.get("appttime", ""),
        "callmorning": call_morning,
        "callafternoon": call_afternoon,
        "callevening": call_evening,
        "phone": appointment_data.get("phone", ""),
        "email": appointment_data.get("email", ""),
        "address": appointment_data.get("address", ""),
        "city": appointment_data.get("city", ""),
        "postal_code": appointment_data.get("postal_code", ""),
    }

    booking_url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(booking_url, headers=headers, data=booking_payload)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
