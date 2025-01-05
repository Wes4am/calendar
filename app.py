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
    print("Request Data Received:", request_data)

    access_token = request_data.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token is missing"}), 400

    # Build the payload to send to the external API
    payload = {
        # Name-related fields
        "prefix": request_data.get("prefix", ""),  # Optional
        "firstname": request_data.get("firstname"),
        "lastname": request_data.get("lastname"),
        "suffix": request_data.get("suffix", ""),  # Optional
        
        # Address fields
        "address1": request_data.get("address1", ""),  # Optional
        "address2": request_data.get("address2", ""),  # Optional
        "city": request_data.get("city", ""),  # Optional
        "state": request_data.get("state", ""),  # Optional
        "zip": request_data.get("zip"),
        "crossStreet": request_data.get("crossStreet", ""),  # Optional

        # Phone-related fields
        "phone": request_data.get("phone"),
        "phonetype": request_data.get("phonetype", 0),  # Optional
        "phone2": request_data.get("phone2", ""),  # Optional
        "phonetype2": request_data.get("phonetype2", 0),  # Optional
        "phone3": request_data.get("phone3", ""),  # Optional
        "phonetype3": request_data.get("phonetype3", 0),  # Optional

        # Product-related fields
        "productID": request_data.get("productID", ""),  # Optional
        "proddescr": request_data.get("proddescr", ""),  # Optional

        # Contact fields
        "email": request_data.get("email", ""),
        "sender": request_data.get("sender", ""),  # Optional
        "lognumber": request_data.get("lognumber", ""),  # Optional
        "sentto": request_data.get("sentto", ""),  # Optional

        # Scheduling and call preferences
        "callmorning": request_data.get("callmorning", False),  # Optional
        "callafternoon": request_data.get("callafternoon", False),  # Optional
        "callevening": request_data.get("callevening", False),  # Optional
        "callweekend": request_data.get("callweekend", False),  # Optional
        "apptdate": request_data.get("apptdate"),
        "appttime": request_data.get("appttime"),
        "datereceived": request_data.get("datereceived", ""),  # Optional

        # Lead source and rank
        "source": request_data.get("source", ""),  # Optional
        "srs_id": request_data.get("srs_id", 0),  # Optional
        "forceSource": request_data.get("forceSource", False),  # Optional
        "brn_id": request_data.get("brn_id", ""),  # Optional
        "rnk_id": request_data.get("rnk_id", 0),  # Optional

        # Miscellaneous
        "notes": request_data.get("notes", ""),  # Optional
        "waiver": request_data.get("waiver", False),  # Optional
        "qnum": request_data.get("qnum", 0),  # Optional
    }

    url = "https://apitest.leadperfection.com/api/Leads/LeadAdd"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print("Payload Sent to External API:", payload)
    print("Headers Sent to External API:", headers)

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        print(f"Error during API call: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
