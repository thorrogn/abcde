import requests
from flask import Flask, jsonify
# Removed request import as the API endpoint will no longer get lat/lng from client query parameters
import geocoder # Added geocoder import to get server's location

app = Flask(__name__)

# Replace with your actual Ambee API key
# It's better to use environment variables in production
# Keeping the original key as it was part of the section to rewrite
API_KEY = '0a0fa0a959d49d0a4f56aac17ed1f4aaa84fa14ac26c26d2377cb1ef58d15718'

# Ambee API endpoint template
AMBEE_API_URL_TEMPLATE = 'https://api.ambeedata.com/weather/latest/by-lat-lng?lat={lat}&lng={lng}'

# Headers for the Ambee API request
AMBEE_HEADERS = {
    'x-api-key': API_KEY,
    'Content-type': 'application/json'
}

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetches the latest weather data for the server's location using Geocoder.ip.
    This endpoint no longer expects lat/lng query parameters from the client.
    It uses the server's IP address to determine location.
    """
    latitude = None
    longitude = None

    # Use geocoder to get the server's location based on its IP
    # This replaces the original logic that expected client input or used hardcoded values
    print("Attempting to fetch server location using IP address...")
    g = geocoder.ip('me')

    # Check if the location was successfully fetched and has lat/lng
    if g.ok and g.latlng:
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        print(f"Fetched server location: Latitude={latitude}, Longitude={longitude}")
    else:
        # If geocoder fails, return an error response to the client
        print("Could not fetch server location using IP address.")
        return jsonify({"error": "Failed to determine server location using IP address."}), 500

    # Use the obtained latitude and longitude to call the Ambee API
    # The rest of the API calling logic remains similar

    try:
        # Construct the API URL using the fetched location
        url = AMBEE_API_URL_TEMPLATE.format(lat=latitude, lng=longitude)

        # Make the request to Ambee API
        response = requests.get(url, headers=AMBEE_HEADERS)

        # Check for successful response from Ambee
        if response.status_code == 200:
            data = response.json()
            # Return the data from Ambee API to the client
            # As before, return the whole JSON response from Ambee
            return jsonify(data), 200
        else:
            # Handle errors from Ambee API response
            error_message = f"Error calling Ambee API: {response.status_code}"
            try:
                error_details = response.json()
                return jsonify({"error": error_message, "details": error_details}), response.status_code
            except requests.exceptions.JSONDecodeError:
                 # If Ambee returns non-JSON error response
                return jsonify({"error": error_message, "details": response.text}), response.status_code

    except requests.exceptions.RequestException as e:
        # Handle network or other request-related errors when calling Ambee API
        return jsonify({"error": "Failed to connect to Ambee API", "details": str(e)}), 500
    except Exception as e:
        # Catch any other unexpected errors during the process
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask development server
    # In production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True, port=5050) # debug=True should be False in production
