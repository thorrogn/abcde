from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import xmltodict
import json
import yaml
from datetime import datetime
import os
import time
import threading
import geocoder
from prometheus_client import make_wsgi_app, Counter, Gauge, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ambee API configuration
API_KEY = '0a0fa0a959d49d0a4f56aac17ed1f4aaa84fa14ac26c26d2377cb1ef58d15718'
AMBEE_API_URL_TEMPLATE = 'https://api.ambeedata.com/weather/latest/by-lat-lng?lat={lat}&lng={lng}'
AMBEE_HEADERS = {
    'x-api-key': API_KEY,
    'Content-type': 'application/json'
}

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
GDACS_ALERTS_GAUGE = Gauge('gdacs_alerts_count', 'Number of GDACS alerts fetched')
RELIEFWEB_DISASTERS_GAUGE = Gauge('reliefweb_disasters_count', 'Number of ReliefWeb disasters fetched')
WEATHER_DATA_GAUGE = Gauge('weather_data_present', 'Indicates if weather data is present (1) or not (0)')

# Global data storage
latest_gdacs_alerts = []
latest_reliefweb_disasters = []
latest_weather_data = None
last_updated = None
last_weather_updated = None

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/gdacs', methods=['GET'])
def get_gdacs_alerts():
    """Get GDACS disaster alerts"""
    GDACS_ALERTS_GAUGE.set(len(latest_gdacs_alerts))
    return jsonify({
        "success": True,
        "data": latest_gdacs_alerts,
        "count": len(latest_gdacs_alerts),
        "last_updated": last_updated.isoformat() if last_updated else None
    })

@app.route('/api/reliefweb', methods=['GET'])
def get_reliefweb_disasters():
    """Get ReliefWeb disaster data"""
    RELIEFWEB_DISASTERS_GAUGE.set(len(latest_reliefweb_disasters))
    return jsonify({
        "success": True,
        "data": latest_reliefweb_disasters,
        "count": len(latest_reliefweb_disasters),
        "last_updated": last_updated.isoformat() if last_updated else None
    })

@app.route('/api/disasters', methods=['GET'])
def get_all_disasters():
    """Get combined disaster data from all sources"""
    combined_disasters = []
    
    # Process GDACS alerts
    for alert in latest_gdacs_alerts:
        combined_disasters.append({
            "id": f"gdacs-{alert.get('guid', len(combined_disasters))}",
            "type": alert.get('alertlevel', 'Unknown'),
            "severity": get_severity_from_alert_level(alert.get('alertlevel', '')),
            "title": alert.get('title', 'GDACS Alert'),
            "description": alert.get('description', 'No description available')[:200] + '...',
            "location": alert.get('country', 'Unknown Location'),
            "coordinates": parse_coordinates(alert.get('coordinates')),
            "timestamp": alert.get('pubDate', datetime.utcnow().isoformat()),
            "source": "GDACS",
            "url": alert.get('link', '')
        })
    
    # Process ReliefWeb disasters
    for disaster in latest_reliefweb_disasters:
        fields = disaster.get('fields', {})
        combined_disasters.append({
            "id": f"reliefweb-{disaster.get('id', len(combined_disasters))}",
            "type": fields.get('type', [{}])[0].get('name', 'Disaster') if fields.get('type') else 'Disaster',
            "severity": "Medium",  # ReliefWeb doesn't provide severity levels
            "title": fields.get('name', 'Disaster Alert'),
            "description": (fields.get('description', 'No description available')[:200] + '...') if fields.get('description') else 'No description available',
            "location": fields.get('country', [{}])[0].get('name', 'Unknown Location') if fields.get('country') else 'Unknown Location',
            "coordinates": None,  # ReliefWeb doesn't always provide coordinates
            "timestamp": fields.get('date', {}).get('created', datetime.utcnow().isoformat()),
            "source": "ReliefWeb",
            "url": fields.get('url_alias', '')
        })
    
    # Sort by timestamp (most recent first)
    combined_disasters.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        "success": True,
        "data": combined_disasters,
        "count": len(combined_disasters),
        "sources": {
            "gdacs": len(latest_gdacs_alerts),
            "reliefweb": len(latest_reliefweb_disasters)
        },
        "last_updated": last_updated.isoformat() if last_updated else None
    })

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather data for specified coordinates or server location"""
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    if lat and lng:
        # Get weather for specific coordinates
        try:
            lat = float(lat)
            lng = float(lng)
            weather_data = fetch_weather_for_coordinates(lat, lng)
            if weather_data:
                return jsonify({
                    "success": True,
                    "data": weather_data,
                    "coordinates": {"lat": lat, "lng": lng},
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to fetch weather data for specified coordinates"
                }), 500
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Invalid coordinates provided"
            }), 400
    else:
        # Return cached server location weather
        if latest_weather_data:
            WEATHER_DATA_GAUGE.set(1)
            return jsonify({
                "success": True,
                "data": latest_weather_data,
                "last_updated": last_weather_updated.isoformat() if last_weather_updated else None
            })
        else:
            WEATHER_DATA_GAUGE.set(0)
            return jsonify({
                "success": False,
                "error": "Weather data not yet available or failed to fetch"
            }), 503

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and data counts"""
    return jsonify({
        "success": True,
        "status": "operational",
        "data": {
            "gdacs_alert_count": len(latest_gdacs_alerts),
            "reliefweb_disaster_count": len(latest_reliefweb_disasters),
            "total_disasters": len(latest_gdacs_alerts) + len(latest_reliefweb_disasters),
            "weather_available": latest_weather_data is not None,
            "last_updated": last_updated.isoformat() if last_updated else None,
            "last_weather_updated": last_weather_updated.isoformat() if last_weather_updated else None
        }
    })

# Helper functions
def get_severity_from_alert_level(alert_level):
    """Convert GDACS alert level to severity"""
    if not alert_level:
        return "Medium"
    
    alert_level = alert_level.lower()
    if 'red' in alert_level:
        return "High"
    elif 'orange' in alert_level:
        return "Medium"
    elif 'green' in alert_level:
        return "Low"
    else:
        return "Medium"

def parse_coordinates(coord_string):
    """Parse coordinate string to lat/lng object"""
    if not coord_string:
        return None
    
    try:
        # Assuming format "lat lng"
        parts = coord_string.strip().split()
        if len(parts) >= 2:
            return {
                "lat": float(parts[0]),
                "lng": float(parts[1])
            }
    except (ValueError, IndexError):
        pass
    
    return None

def fetch_weather_for_coordinates(lat, lng):
    """Fetch weather data for specific coordinates"""
    try:
        url = AMBEE_API_URL_TEMPLATE.format(lat=lat, lng=lng)
        response = requests.get(url, headers=AMBEE_HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return format_weather_data(data)
        else:
            print(f"Weather API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def format_weather_data(raw_data):
    """Format weather data from Ambee API"""
    try:
        if 'data' in raw_data:
            weather = raw_data['data']
            return {
                "temperature": weather.get('temperature', 0),
                "humidity": weather.get('humidity', 0),
                "windSpeed": weather.get('windSpeed', 0),
                "conditions": weather.get('summary', 'Unknown'),
                "pressure": weather.get('pressure', 0),
                "visibility": weather.get('visibility', 0)
            }
        else:
            # Fallback format
            return {
                "temperature": raw_data.get('temperature', 0),
                "humidity": raw_data.get('humidity', 0),
                "windSpeed": raw_data.get('windSpeed', 0),
                "conditions": raw_data.get('summary', 'Unknown'),
                "pressure": raw_data.get('pressure', 0),
                "visibility": raw_data.get('visibility', 0)
            }
    except Exception as e:
        print(f"Error formatting weather data: {e}")
        return {
            "temperature": 0,
            "humidity": 0,
            "windSpeed": 0,
            "conditions": "Unknown",
            "pressure": 0,
            "visibility": 0
        }

# Data fetching functions
def load_config(filepath):
    """Load configuration from YAML file"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_filepath = os.path.join(script_dir, filepath)
        if not os.path.exists(full_filepath):
            print(f"[✘] Configuration file not found at {full_filepath}")
            return None
        with open(full_filepath, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"[✘] Error loading config {filepath}: {e}")
        return None

def fetch_gdacs(config):
    """Fetch GDACS disaster alerts"""
    global latest_gdacs_alerts, last_updated
    
    try:
        url = config.get('gdacs_url')
        relevant_fields_config = config.get('relevant_fields', [])
        max_alerts_to_process = config.get('max_alerts_to_process', 20)
        
        print(f"[*] Fetching GDACS data from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data_dict = xmltodict.parse(response.content)
        alerts = data_dict.get('rss', {}).get('channel', {}).get('item', [])
        
        if not isinstance(alerts, list):
            alerts = [alerts] if alerts else []
        
        relevant_alerts = []
        alerts_to_process = alerts[:min(len(alerts), max_alerts_to_process)]
        
        for alert in alerts_to_process:
            relevant_data = {}
            for field in relevant_fields_config:
                if field == 'guid':
                    relevant_data[field] = alert.get('guid', {}).get('#text') if isinstance(alert.get('guid'), dict) else alert.get('guid')
                elif field == 'population':
                    relevant_data[field] = alert.get('gdacs:population', {}).get('#text') if isinstance(alert.get('gdacs:population'), dict) else alert.get('gdacs:population')
                elif field == 'vulnerability':
                    relevant_data[field] = alert.get('gdacs:vulnerability', {}).get('#text') if isinstance(alert.get('gdacs:vulnerability'), dict) else alert.get('gdacs:vulnerability')
                elif field == 'coordinates':
                    relevant_data[field] = alert.get('georss:point')
                else:
                    value = alert.get(f"gdacs:{field}")
                    if value is None:
                        value = alert.get(field)
                    relevant_data[field] = value
            
            relevant_alerts.append(relevant_data)
        
        latest_gdacs_alerts = relevant_alerts
        last_updated = datetime.utcnow()
        GDACS_ALERTS_GAUGE.set(len(latest_gdacs_alerts))
        
        print(f"[✔] GDACS alerts updated: {len(latest_gdacs_alerts)} alerts")
        
    except Exception as e:
        print(f"[✘] Error fetching GDACS data: {e}")

def fetch_reliefweb(config):
    """Fetch ReliefWeb disaster data"""
    global latest_reliefweb_disasters, last_updated
    
    try:
        api_conf = config.get("api", {})
        query_conf = config.get("query", {})
        
        scheme = api_conf.get("scheme", "https")
        host = api_conf.get("host", "api.reliefweb.int")
        path = api_conf.get("path", "/v1/disasters")
        base_url = f"{scheme}://{host}{path}"
        
        params = {
            "appname": api_conf.get("appname", "disaster-management-app"),
            "limit": query_conf.get("limit", 20),
            "profile": query_conf.get("profile", "full"),
        }
        
        sort_fields = query_conf.get("sort")
        if isinstance(sort_fields, list) and sort_fields:
            params["sort[]"] = sort_fields
        
        filters = query_conf.get("filters", {})
        if isinstance(filters, dict):
            for key, value in filters.items():
                if value is not None and value != "":
                    params[f"filter[field][{key}]"] = value
        
        print(f"[*] Fetching ReliefWeb data from: {base_url}")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        disasters = data.get("data", [])
        
        latest_reliefweb_disasters = disasters
        last_updated = datetime.utcnow()
        RELIEFWEB_DISASTERS_GAUGE.set(len(latest_reliefweb_disasters))
        
        print(f"[✔] ReliefWeb disasters updated: {len(latest_reliefweb_disasters)} disasters")
        
    except Exception as e:
        print(f"[✘] Error fetching ReliefWeb data: {e}")

def fetch_weather():
    """Fetch weather data for server location"""
    global latest_weather_data, last_weather_updated
    
    try:
        print("[*] Fetching server location for weather...")
        g = geocoder.ip('me')
        
        if g.ok and g.latlng:
            latitude, longitude = g.latlng
            print(f"[*] Server location: {latitude}, {longitude}")
            
            weather_data = fetch_weather_for_coordinates(latitude, longitude)
            if weather_data:
                latest_weather_data = weather_data
                last_weather_updated = datetime.utcnow()
                WEATHER_DATA_GAUGE.set(1)
                print("[✔] Weather data updated")
            else:
                print("[✘] Failed to fetch weather data")
        else:
            print("[✘] Could not determine server location")
            
    except Exception as e:
        print(f"[✘] Error fetching weather: {e}")

def periodic_fetch():
    """Periodically fetch data from all sources"""
    disaster_interval = 300  # 5 minutes
    weather_interval = 900   # 15 minutes
    last_weather_fetch = 0
    
    while True:
        try:
            current_time = time.time()
            print(f"\n[*] Starting data fetch cycle at {datetime.utcnow().isoformat()}")
            
            # Fetch weather data less frequently
            if current_time - last_weather_fetch >= weather_interval:
                fetch_weather()
                last_weather_fetch = current_time
            
            # Load configs and fetch disaster data
            gdacs_config = load_config("gdacs_config.yaml")
            reliefweb_config = load_config("reliefweb_config.yaml")
            
            if gdacs_config:
                fetch_gdacs(gdacs_config)
            
            if reliefweb_config:
                fetch_reliefweb(reliefweb_config)
            
            print(f"[*] Data fetch cycle complete. Next cycle in {disaster_interval} seconds.")
            time.sleep(disaster_interval)
            
        except Exception as e:
            print(f"[✘] Error in periodic fetch: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

# Initialize data on startup
def initialize_data():
    """Initialize data on application startup"""
    print("[*] Initializing application data...")
    
    # Load initial data
    gdacs_config = load_config("gdacs_config.yaml")
    reliefweb_config = load_config("reliefweb_config.yaml")
    
    if gdacs_config:
        fetch_gdacs(gdacs_config)
    
    if reliefweb_config:
        fetch_reliefweb(reliefweb_config)
    
    fetch_weather()
    
    print("[*] Initial data load complete")

if __name__ == '__main__':
    # Initialize data
    initialize_data()
    
    # Start background data fetching thread
    print("[*] Starting background data fetching...")
    fetch_thread = threading.Thread(target=periodic_fetch, daemon=True)
    fetch_thread.start()
    
    # Start Flask server
    print("[*] Starting Flask server on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
