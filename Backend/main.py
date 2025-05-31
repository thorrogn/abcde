import requests
import xmltodict
import json
import yaml
from datetime import datetime
import os

# Create timestamp for file naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def load_config(filepath):
    """Loads configuration from a YAML file."""
    try:
        # Ensure path is relative to the project root if necessary, assuming script is in Disaster-Management
        # Use a robust way to get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_filepath = os.path.join(script_dir, filepath)
        # Check if the file exists before trying to open it
        if not os.path.exists(full_filepath):
            print(f"[✘] Configuration file not found at {full_filepath}")
            return None
        with open(full_filepath, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        # This block might be redundant due to the os.path.exists check, but keeping for safety
        print(f"[✘] Configuration file not found at {filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"[✘] Error parsing YAML configuration file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"[✘] An unexpected error occurred loading config {filepath}: {e}")
        return None

def create_output_directory(directory_path):
    """Creates a directory if it doesn't exist."""
    # Use a robust way to get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_directory_path = os.path.join(script_dir, directory_path)
    try:
        os.makedirs(full_directory_path, exist_ok=True)
        print(f"[*] Ensured directory exists: {directory_path}")
    except OSError as e:
        print(f"[✘] Error creating directory {directory_path}: {e}")
        # Depending on severity, you might want to raise the exception
        return False
    return True

def fetch_gdacs(config):
    """Fetches, parses, and saves relevant GDACS alerts data based on config."""
    url = config.get('gdacs_url')
    if not url:
        print("[✘] GDACS URL not found in the configuration.")
        return

    relevant_fields_config = config.get('relevant_fields')
    if not isinstance(relevant_fields_config, list) or not relevant_fields_config:
        print("[✘] 'relevant_fields' must be a non-empty list in GDACS configuration.")
        return

    max_alerts_to_process = config.get('max_alerts_to_process', float('inf')) # Use float('inf') if not set to process all

    # Define output directory
    output_dir = "JSON/gdacs"
    if not create_output_directory(output_dir):
        print(f"[✘] Could not create output directory {output_dir}. Skipping GDACS data saving.")
        return

    try:
        print(f"[*] Fetching GDACS data from: {url}")
        response = requests.get(url)
        response.raise_for_status()

        # Convert XML to Python dict
        data_dict = xmltodict.parse(response.content)

        # Extract alerts (list of disaster events)
        alerts = data_dict.get('rss', {}).get('channel', {}).get('item', [])

        if not alerts:
            print("[!] No GDACS alerts found in the feed.")
            # Decide if you want to save an empty file or not
            # Let's save an empty list to indicate no data was found
            relevant_alerts = []
        else:
            # Process alerts to extract only relevant information, limited by config
            relevant_alerts = []
            # Ensure we don't try to slice more than the number of alerts available
            alerts_to_process = alerts[:min(len(alerts), max_alerts_to_process)]

            print(f"[*] Processing up to {len(alerts_to_process)} GDACS alerts...")

            for alert in alerts_to_process:
                relevant_data = {}
                for field in relevant_fields_config:
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
                        # Default extraction for other fields (handles gdacs: prefixed tags implicitly if present)
                        # Also try without gdacs prefix for general fields
                        value = alert.get(f"gdacs:{field}")
                        if value is None:
                             value = alert.get(field)
                        relevant_data[field] = value

                relevant_alerts.append(relevant_data)


        # Save relevant GDACS alerts to JSON
        gdacs_filename = f"gdacs_alerts_relevant_{timestamp}.json"
        # Construct the full output path including the new directory
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir, gdacs_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(relevant_alerts, f, ensure_ascii=False, indent=4)

        print(f"[✔] Relevant GDACS alerts saved to {os.path.join(output_dir, gdacs_filename)}")

    except requests.exceptions.RequestException as e:
        print(f"[✘] Error fetching GDACS data: {e}")
    except Exception as e:
        print(f"[✘] An unexpected error occurred fetching GDACS data: {e}")

def fetch_reliefweb(config):
    """Fetches and prints ReliefWeb disaster data based on config, and saves to JSON."""
    api_conf = config.get("api")
    query_conf = config.get("query")
    output_conf = config.get("output")

    if not api_conf or not query_conf or not output_conf:
        print("[✘] Missing 'api', 'query', or 'output' sections in ReliefWeb configuration.")
        return

    # Define output directory
    output_dir = "JSON/relief"
    if not create_output_directory(output_dir):
        print(f"[✘] Could not create output directory {output_dir}. Skipping ReliefWeb data saving.")
        return


    # Build base URL
    scheme = api_conf.get("scheme", "https")
    host = api_conf.get("host", "api.reliefweb.int")
    path = api_conf.get("path", "/v1/disasters")
    base_url = f"{scheme}://{host}{path}"

    # Build query parameters
    params = {
        "appname": api_conf.get("appname", "default-app"),
        "limit": query_conf.get("limit", 10), # Default limit
        "profile": query_conf.get("profile", "basic"), # Default profile
    }

    sort_fields = query_conf.get("sort")
    if isinstance(sort_fields, list) and sort_fields:
        params["sort[]"] = sort_fields
    elif sort_fields:
        print("[!] 'sort' in ReliefWeb config should be a list. Ignoring sort.")


    # Add optional filters
    filters = query_conf.get("filters", {})
    if isinstance(filters, dict):
        for key, value in filters.items():
            # Check if value is not None or empty string before adding to params
            if value is not None and value != "":
                params[f"filter[field][{key}]"] = value
    else:
         print("[!] 'filters' in ReliefWeb config should be a dictionary. Ignoring filters.")

    try:
        print(f"[*] Fetching ReliefWeb data from: {base_url}")
        # print(f"[*] With parameters: {params}") # Uncomment for debugging params
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        disasters = data.get("data", [])

        if not disasters:
            print("[!] No ReliefWeb disasters found.")
            # Even if no disasters are found, we might want to save an empty list
            # depending on desired behavior. Let's save an empty list.
            print("[*] Saving an empty list to ReliefWeb JSON file.")


        print(f"[*] Processing {len(disasters)} ReliefWeb disasters...")

        # Save ReliefWeb disasters to JSON
        reliefweb_filename = f"reliefweb_disasters_{timestamp}.json"
        # Construct the full output path including the new directory
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir, reliefweb_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(disasters, f, ensure_ascii=False, indent=4)

        print(f"[✔] ReliefWeb disasters saved to {os.path.join(output_dir, reliefweb_filename)}")

        # Continue with printing based on output_fields if disasters were found
        if disasters:
            output_fields = output_conf.get("fields")

            print("\n[*] ReliefWeb disaster summaries based on output fields:")
            for disaster in disasters:
                fields = disaster.get("fields", {})
                if output_fields is not None and isinstance(output_fields, list): # Check if fields is explicitly defined (even empty list)
                    if output_fields:
                        for field in output_fields:
                            print(f"{field}: {fields.get(field)}")
                else: # Default behavior if output_fields is missing or not a list
                    print("[*] Printing all available fields:")
                    # Print all fields if 'fields' is not specified or not a list
                    for field_name, field_value in fields.items():
                         print(f"{field_name}: {field_value}")

                print("-" * 60) # Use a different separator for individual disasters

    except requests.exceptions.RequestException as e:
        print(f"[✘] Error fetching ReliefWeb data: {e}")
    except json.JSONDecodeError:
         print(f"[✘] Error decoding JSON response from ReliefWeb.\nResponse content: {response.text[:500]}...") # Print part of response for debugging
    except Exception as e:
        print(f"[✘] An unexpected error occurred fetching ReliefWeb data: {e}")


    # Build base URL
    scheme = api_conf.get("scheme", "https")
    host = api_conf.get("host", "api.reliefweb.int")
    path = api_conf.get("path", "/v1/disasters")
    base_url = f"{scheme}://{host}{path}"

    # Build query parameters
    params = {
        "appname": api_conf.get("appname", "default-app"),
        "limit": query_conf.get("limit", 10), # Default limit
        "profile": query_conf.get("profile", "basic"), # Default profile
    }

    sort_fields = query_conf.get("sort")
    if isinstance(sort_fields, list) and sort_fields:
        params["sort[]"] = sort_fields
    elif sort_fields:
        print("[!] 'sort' in ReliefWeb config should be a list. Ignoring sort.")


    # Add optional filters
    filters = query_conf.get("filters", {})
    if isinstance(filters, dict):
        for key, value in filters.items():
            # Check if value is not None or empty string before adding to params
            if value is not None and value != "":
                params[f"filter[field][{key}]"] = value
    else:
         print("[!] 'filters' in ReliefWeb config should be a dictionary. Ignoring filters.")

    try:
        print(f"[*] Fetching ReliefWeb data from: {base_url}")
        # print(f"[*] With parameters: {params}") # Uncomment for debugging params
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        disasters = data.get("data", [])

        if not disasters:
            print("[!] No ReliefWeb disasters found.")
            # Even if no disasters are found, we might want to save an empty list
            # depending on desired behavior. Let's save an empty list.
            print("[*] Saving an empty list to ReliefWeb JSON file.")


        print(f"[*] Processing {len(disasters)} ReliefWeb disasters...")

        # Save ReliefWeb disasters to JSON
        reliefweb_filename = f"reliefweb_disasters_{timestamp}.json"
        # Construct the full output path including the new directory
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir, reliefweb_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(disasters, f, ensure_ascii=False, indent=4)

        print(f"[✔] ReliefWeb disasters saved to {os.path.join(output_dir, reliefweb_filename)}")

        # Continue with printing based on output_fields if disasters were found
        if disasters:
            output_fields = output_conf.get("fields")

            print("\n[*] ReliefWeb disaster summaries based on output fields:")
            for disaster in disasters:
                fields = disaster.get("fields", {})
                if output_fields is not None and isinstance(output_fields, list): # Check if fields is explicitly defined (even empty list)
                    if output_fields:
                        for field in output_fields:
                            print(f"{field}: {fields.get(field)}")
                else: # Default behavior if output_fields is missing or not a list
                    print("[*] Printing all available fields:")
                    # Print all fields if 'fields' is not specified or not a list
                    for field_name, field_value in fields.items():
                         print(f"{field_name}: {field_value}")

                print("-" * 60) # Use a different separator for individual disasters

    except requests.exceptions.RequestException as e:
        print(f"[✘] Error fetching ReliefWeb data: {e}")
    except json.JSONDecodeError:
         print(f"[✘] Error decoding JSON response from ReliefWeb.\nResponse content: {response.text[:500]}...") # Print part of response for debugging
    except Exception as e:
        print(f"[✘] An unexpected error occurred fetching ReliefWeb data: {e}")


# ========== RUN SCRIPT ==========\n
if __name__ == "__main__":
    print("🔄 Fetching real-time disaster alerts...")

    # Load and process GDACS configuration and data
    print("\n--- GDACS Data Fetch ---")
    # Assuming gdacs_config.yaml is in the same directory as the script
    gdacs_config = load_config("gdacs_config.yaml")

    if gdacs_config:
        # Basic validation for GDACS config fields
        if 'gdacs_url' in gdacs_config and isinstance(gdacs_config.get('relevant_fields'), list):
             # Check for max_alerts_to_process explicitly as it has a default
             if 'max_alerts_to_process' in gdacs_config and not isinstance(gdacs_config['max_alerts_to_process'], (int, float)):
                 print("[!] 'max_alerts_to_process' in GDACS config should be a number. Using default.")
                 # No need to set to default here, the get method with default handles it.
             fetch_gdacs(gdacs_config)
        else:
             print("[✘] GDACS configuration is missing required fields or 'relevant_fields' is not a list. Skipping GDACS fetch.")
             print(f"GDACS config content: {gdacs_config}") # Print config for debugging
    else:
        print("[✘] Failed to load GDACS configuration. Skipping GDACS fetch.")

    print("\n" + "=" * 60 + "\n") # Separator

    # Load and process ReliefWeb configuration and data
    print("--- ReliefWeb Data Fetch ---")
    # Assuming reliefweb_config.yaml is in the same directory as the script
    reliefweb_config = load_config("reliefweb_config.yaml")

    if reliefweb_config:
        # Basic validation for ReliefWeb config sections
        if 'api' in reliefweb_config and 'query' in reliefweb_config and 'output' in reliefweb_config:
            fetch_reliefweb(reliefweb_config)
        else:
            print("[✘] ReliefWeb configuration is missing 'api', 'query', or 'output' sections. Skipping ReliefWeb fetch.")
            print(f"ReliefWeb config content: {reliefweb_config}") # Print config for debugging
    else:
        print("[✘] Failed to load ReliefWeb configuration. Skipping ReliefWeb fetch.")

    print("\nProcessing complete.")
