import requests
import xmltodict
import json
import yaml
from datetime import datetime
import os
import time
from flask import Flask, jsonify
import threading
import geocoder
from prometheus_client import make_wsgi_app, Counter, Gauge, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import REGISTRY

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


latest_gdacs_alerts = []
latest_reliefweb_disasters = []
latest_weather_data = None
last_updated = None
last_weather_updated = None

app = Flask(__name__)

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

@app.route('/gdacs', methods=['GET'])
def get_gdacs_alerts():
    GDACS_ALERTS_GAUGE.set(len(latest_gdacs_alerts))
    return jsonify({
        "data": latest_gdacs_alerts,
        "last_updated_utc": last_updated.isoformat() if last_updated else None
    })

@app.route('/reliefweb', methods=['GET'])
def get_reliefweb_disasters():
    RELIEFWEB_DISASTERS_GAUGE.set(len(latest_reliefweb_disasters))
    return jsonify({
        "data": latest_reliefweb_disasters,
        "last_updated_utc": last_updated.isoformat() if last_updated else None
    })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "gdacs_alert_count": len(latest_gdacs_alerts),
        "reliefweb_disaster_count": len(latest_reliefweb_disasters),
        "last_updated_utc": last_updated.isoformat() if last_updated else None,
        "last_weather_updated_utc": last_weather_updated.isoformat() if last_weather_updated else None
    })

@app.route('/weather', methods=['GET'])
def get_weather():
    if latest_weather_data:
        WEATHER_DATA_GAUGE.set(1)
        return jsonify({
            "data": latest_weather_data,
            "last_updated_utc": last_weather_updated.isoformat() if last_weather_updated else None
        }), 200
    else:
        WEATHER_DATA_GAUGE.set(0)
        return jsonify({"error": "Weather data not yet available or failed to fetch."}), 503

def load_config(filepath):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_filepath = os.path.join(script_dir, filepath)
    with open(full_filepath, 'r') as f:
        config = yaml.safe_load(f)
    return config

def create_output_directory(directory_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_directory_path = os.path.join(script_dir, directory_path)
    os.makedirs(full_directory_path, exist_ok=True)
    print(f"[*] Ensured directory exists: {directory_path}")
    return True

def fetch_gdacs(config):
    global latest_gdacs_alerts, last_updated

    url = config.get('gdacs_url')
    relevant_fields_config = config.get('relevant_fields')
    max_alerts_to_process = config.get('max_alerts_to_process', float('inf'))
    output_dir = "JSON/gdacs"
    create_output_directory(output_dir)

    print(f"[*] Fetching GDACS data from: {url}")
    response = requests.get(url)
    data_dict = xmltodict.parse(response.content)
    alerts = data_dict.get('rss', {}).get('channel', {}).get('item', [])

    if not alerts:
        relevant_alerts = []
    else:
        relevant_alerts = []
        alerts_to_process = alerts[:min(len(alerts), max_alerts_to_process)]
        print(f"[*] Processing up to {len(alerts_to_process)} GDACS alerts...")

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

    print(f"[✔] GDACS alerts data updated in memory. Fetched {len(latest_gdacs_alerts)} alerts.")

def fetch_reliefweb(config):
    global latest_reliefweb_disasters, last_updated

    api_conf = config.get("api")
    query_conf = config.get("query")
    output_conf = config.get("output")
    output_dir = "JSON/relief"
    create_output_directory(output_dir)

    scheme = api_conf.get("scheme", "https")
    host = api_conf.get("host", "api.reliefweb.int")
    path = api_conf.get("path", "/v1/disasters")
    base_url = f"{scheme}://{host}{path}"

    params = {
        "appname": api_conf.get("appname", "default-app"),
        "limit": query_conf.get("limit", 10),
        "profile": query_conf.get("profile", "basic"),
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
    response = requests.get(base_url, params=params)
    data = response.json()
    disasters = data.get("data", [])

    print(f"[*] Processed {len(disasters)} ReliefWeb disasters.")
    latest_reliefweb_disasters = disasters
    last_updated = datetime.utcnow()
    RELIEFWEB_DISASTERS_GAUGE.set(len(latest_reliefweb_disasters))

    print(f"[✔] ReliefWeb disaster data updated in memory. Fetched {len(latest_reliefweb_disasters)} disasters.")

    if disasters:
        output_fields = output_conf.get("fields")
        if output_fields is not None:
             print("\n[*] ReliefWeb disaster summaries based on output fields:")
             for disaster in disasters:
                fields = disaster.get("fields", {})
                if isinstance(output_fields, list) and output_fields:
                    for field in output_fields:
                        print(f"{field}: {fields.get(field)}")
                elif not output_fields:
                     print("[*] 'output.fields' is empty, skipping console summary.")
                     break
                else:
                     print("[*] Printing all available fields:")
                     for field_name, field_value in fields.items():
                          print(f"{field_name}: {field_value}")
                print("-" * 60)
        else:
            print("[*] 'output.fields' not specified in config, skipping console summary.")

def fetch_weather():
    global latest_weather_data, last_weather_updated

    latitude = None
    longitude = None

    print("\n[*] Attempting to fetch server location using IP address for weather...")
    g = geocoder.ip('me')

    if g.ok and g.latlng:
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        print(f"[*] Fetched server location: Latitude={latitude}, Longitude={longitude}")
    else:
        print("[✘] Could not fetch server location using IP address for weather.")
        latest_weather_data = {"error": "Failed to determine server location using IP address."}
        last_weather_updated = datetime.utcnow()
        return

    url = AMBEE_API_URL_TEMPLATE.format(lat=latitude, lng=longitude)
    print(f"[*] Fetching weather data from Ambee API: {url}")
    response = requests.get(url, headers=AMBEE_HEADERS)
    data = response.json()
    latest_weather_data = data
    last_weather_updated = datetime.utcnow()
    WEATHER_DATA_GAUGE.set(1 if latest_weather_data else 0)
    print(f"[✔] Weather data updated in memory.")

def periodic_fetch(disaster_fetch_interval_seconds, weather_fetch_interval_seconds):
    last_weather_fetch_time = 0

    while True:
        current_time = time.time()
        print("\n" + "=" * 60 + "\n")
        print(f"🔄 Starting periodic data fetch cycle at {datetime.utcnow().isoformat()} UTC...")

        if current_time - last_weather_fetch_time >= weather_fetch_interval_seconds:
             print("\n" + "-" * 30 + " Weather " + "-" * 30 + "\n")
             fetch_weather()
             last_weather_fetch_time = current_time
        else:
             print(f"\n[*] Skipping weather fetch. Next weather fetch in approx {int(weather_fetch_interval_seconds - (current_time - last_weather_fetch_time))} seconds.")

        gdacs_config = load_config("gdacs_config.yaml")
        reliefweb_config = load_config("reliefweb_config.yaml")

        if gdacs_config:
            if 'gdacs_url' in gdacs_config and isinstance(gdacs_config.get('relevant_fields'), list):
                 if 'max_alerts_to_process' in gdacs_config and not isinstance(gdacs_config['max_alerts_to_process'], (int, float)):
                     print("[!] 'max_alerts_to_process' in GDACS config should be a number. Using default.")
                 fetch_gdacs(gdacs_config)
            else:
                 print("[✘] GDACS configuration is missing required fields or 'relevant_fields' is not a list. Skipping GDACS fetch.")
                 print(f"GDACS config content: {gdacs_config}")
        else:
            print("[✘] Failed to load GDACS configuration. Skipping GDACS fetch.")

        print("\n" + "-" * 30 + " ReliefWeb " + "-" * 30 + "\n")

        if reliefweb_config:
            if 'api' in reliefweb_config and 'query' in reliefweb_config and 'output' in reliefweb_config:
                fetch_reliefweb(reliefweb_config)
            else:
                print("[✘] ReliefWeb configuration is missing 'api', 'query', or 'output' sections. Skipping ReliefWeb fetch.")
                print(f"Reliefweb config content: {reliefweb_config}")
        else:
            print("[✘] Failed to load ReliefWeb configuration. Skipping ReliefWeb fetch.")

        print(f"\n[*] Periodic fetch cycle complete.")
        print(f"[*] Waiting {disaster_fetch_interval_seconds} seconds until next disaster data fetch cycle.")
        time.sleep(disaster_fetch_interval_seconds)

if __name__ == "__main__":
    disaster_fetch_interval_seconds = 300
    weather_fetch_interval_seconds = 900

    print("[*] Performing initial data fetch...")
    initial_gdacs_config = load_config("gdacs_config.yaml")
    initial_reliefweb_config = load_config("reliefweb_config.yaml")

    if initial_gdacs_config:
        fetch_gdacs(initial_gdacs_config)

    if initial_reliefweb_config:
        fetch_reliefweb(initial_reliefweb_config)

    fetch_weather()

    print("\n[*] Initial fetch complete.")

    print(f"[*] Starting periodic fetch thread (disaster interval: {disaster_fetch_interval_seconds}s, weather interval: {weather_fetch_interval_seconds}s)...")
    fetch_thread = threading.Thread(target=periodic_fetch, args=(disaster_fetch_interval_seconds, weather_fetch_interval_seconds,), daemon=True)
    fetch_thread.start()

    print("\n[*] Starting Flask web server...")
    try:
        from flask import request
        app.run(debug=True, port=5050, host='0.0.0.0')
    except Exception as e:
        print(f"[✘] Error starting Flask server: {e}")
