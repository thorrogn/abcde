import webbrowser
import geocoder

def open_google_map(lat, lon):
    """
    Opens Google Maps in the default browser at the specified latitude and longitude,
    showing a pin at the location.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        # Zoom level is not directly supported in the /search URL format,
        # but Google Maps will zoom appropriately to the marker.
    """
    # Use the /search?query= format to place a marker on the map
    url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    webbrowser.open(url)

# --- Main Execution ---

# Attempt to get latitude and longitude from user input
user_lat_str = input("Enter latitude (press Enter for current location): ")
user_lon_str = input("Enter longitude (press Enter for current location): ")

latitude = None
longitude = None

try:
    # Try converting user input to float
    if user_lat_str and user_lon_str:
        latitude = float(user_lat_str)
        longitude = float(user_lon_str)
        print(f"Using user provided location: Latitude={latitude}, Longitude={longitude}")
    else:
        raise ValueError("Empty input") # Raise error to fall back to default

except (ValueError, TypeError):
    # If user input is invalid or empty, fall back to current location
    print("Invalid or empty input. Fetching current location using IP address...")
    g = geocoder.ip('me')

    if g.ok: # Check if the location was successfully fetched
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        print(f"Fetched current location: Latitude={latitude}, Longitude={longitude}")
    else:
        print("Could not fetch current location using IP address.")
        print("Please check your network connection or provide coordinates manually.")
        # Exit or handle the error appropriately if no location can be determined
        # For this example, we will not open the map if location fails
        latitude = None
        longitude = None

# Open Google Map if coordinates were successfully determined
if latitude is not None and longitude is not None:
    # Note: The zoom parameter was removed from the open_google_map call
    # as it's not directly supported in the /search URL format used for pins.
    open_google_map(latitude, longitude)
else:
    print("Cannot open map without valid coordinates.")
