from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

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

# API route to handle form submission
@app.route("/submit-form", methods=["POST"])
def submit_form():
    # Get form data from the request
    form_data = request.json  # Assuming the frontend sends JSON
    branch_id = form_data.get("branchid", "")
    product_id = form_data.get("productid", "")
    zip_code = form_data.get("zip", "")

    # Fetch the access token
    access_token = fetch_token()
    if not access_token:
        return jsonify({"error": "Failed to fetch access token"}), 500

    # Prepare data for LeadPerfection API
    lead_api_url = "https://apitest.leadperfection.com/forward-look"  # Replace with the correct endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Data for the LeadPerfection API
    lead_data = {
        "branchid": branch_id,
        "productid": product_id,
        "zip": zip_code
    }

    try:
        # Send the form data to the LeadPerfection API
        response = requests.post(lead_api_url, headers=headers, data=lead_data)
        if response.status_code == 200:
            return jsonify(response.json())  # Return the LeadPerfection API response
        else:
            return jsonify({"error": response.text, "status": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
