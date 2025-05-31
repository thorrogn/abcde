import requests
import xmltodict
import json
import yaml
from datetime import datetime

# Create timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- CONFIGURATION FILE ---
# Create a sample config1.yaml file with required settings
# Example content for config1.yaml:
# gdacs_url: "https://www.gdacs.org/xml/rss.xml"
# max_alerts_to_process: 5
# relevant_fields:
#   - 'title'
#   - 'link'
#   - 'pubDate'
#   - 'description'
#   - 'guid'
#   - 'severity'
#   - 'severitylevel'
#   - 'eventtype'
#   - 'country'
#   - 'population'
#   - 'vulnerability'
#   - 'coordinates' # This maps to georss:point in the XML

def load_config(filepath):
    """Loads configuration from a YAML file."""
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        # Validate necessary fields are present
        required_keys = ['gdacs_url', 'max_alerts_to_process', 'relevant_fields']
        if not all(key in config for key in required_keys):
            raise ValueError(f"Config file must contain keys: {', '.join(required_keys)}")
        if not isinstance(config.get('relevant_fields'), list) or not config.get('relevant_fields'):
             raise ValueError("'relevant_fields' in config must be a non-empty list.")
        return config
    except FileNotFoundError:
        print(f"[✘] Configuration file not found at {filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"[✘] Error parsing YAML configuration file: {e}")
        return None
    except ValueError as e:
        print(f"[✘] Configuration file validation error: {e}")
        return None
    except Exception as e:
        print(f"[✘] An unexpected error occurred loading config: {e}")
        return None


# ========== GDACS FETCH & SAVE ==========
def fetch_gdacs(url, config):
    """Fetches, parses, and saves relevant GDACS alerts data from the given URL,
       limited by config and extracting fields specified in config."""
    try:
        print(f"[*] Fetching data from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        # Convert XML to Python dict
        data_dict = xmltodict.parse(response.content)

        # Extract alerts (list of disaster events)
        alerts = data_dict.get('rss', {}).get('channel', {}).get('item', [])

        if not alerts:
            print("[!] No alerts found in the GDACS feed.")
            return

        # Process alerts to extract only relevant information, limited by config
        relevant_alerts = []
        alerts_to_process = alerts[:config.get('max_alerts_to_process', len(alerts))] # Limit based on config

        print(f"[*] Processing up to {len(alerts_to_process)} alerts...")

        for alert in alerts_to_process:
            relevant_data = {}
            for field in config['relevant_fields']:
                # Special handling for fields that might be nested or have specific XML tags
                if field == 'guid':
                     # Handle GUID which might be dict or string
                    relevant_data[field] = alert.get('guid', {}).get('#text') if isinstance(alert.get('guid'), dict) else alert.get('guid')
                elif field == 'population':
                    # Handle potential nested text for population
                    relevant_data[field] = alert.get('gdacs:population', {}).get('#text') if isinstance(alert.get('gdacs:population'), dict) else alert.get('gdacs:population')
                elif field == 'vulnerability':
                    # Handle potential nested text for vulnerability
                    relevant_data[field] = alert.get('gdacs:vulnerability', {}).get('#text') if isinstance(alert.get('gdacs:vulnerability'), dict) else alert.get('gdacs:vulnerability')
                elif field == 'coordinates':
                     # georss:point format is usually "lat long"
                    relevant_data[field] = alert.get('georss:point')
                else:
                    # Default extraction for other fields (handles gdacs: prefixed tags implicitly)
                    relevant_data[field] = alert.get(f"gdacs:{field}") if field in ['severity', 'severitylevel', 'eventtype', 'country'] else alert.get(field)

            relevant_alerts.append(relevant_data)


        # Save relevant GDACS alerts to JSON
        gdacs_filename = f"gdacs_alerts_relevant_{timestamp}.json"
        with open(gdacs_filename, 'w', encoding='utf-8') as f:
            json.dump(relevant_alerts, f, ensure_ascii=False, indent=4)

        print(f"[✔] Relevant GDACS alerts saved to {gdacs_filename}")

    except requests.exceptions.RequestException as e:
        print(f"[✘] Error fetching GDACS data: {e}")
    except Exception as e:
        print(f"[✘] An unexpected error occurred fetching GDACS data: {e}")


# ========== RUN SCRIPT ==========
if __name__ == "__main__":
    print("🔄 Fetching real-time disaster alerts...")

    # Load configuration from config1.yaml
    config = load_config("config1.yaml")

    if config:
        # Use the URL from the config
        gdacs_url = config.get('gdacs_url')
        if gdacs_url:
            fetch_gdacs(gdacs_url, config)
        else:
            print("[✘] GDACS URL not found in the configuration file.")
    else:
        print("[✘] Failed to load configuration. Aborting.")
