import json
import os
import glob
from datetime import datetime

def find_latest_json(directory, prefix):
    """Finds the latest JSON file in a directory based on a timestamp prefix."""
    # Construct the full pattern to search for, including the timestamp part
    # Assumes timestamp is sortable lexicographically (YYYYMMDD_HHMMSS)
    pattern = os.path.join(directory, f"{prefix}*.json")
    list_of_files = glob.glob(pattern)

    if not list_of_files:
        print(f"[!] No files found matching pattern: {pattern}")
        return None

    # Sort files by name (which includes the timestamp) to get the latest
    latest_file = max(list_of_files)
    return latest_file

def load_json_file(filepath):
    """Loads data from a JSON file."""
    if not os.path.exists(filepath):
        print(f"[✘] File not found: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[*] Successfully loaded data from {filepath}")
        return data
    except json.JSONDecodeError as e:
        print(f"[✘] Error decoding JSON from {filepath}: {e}")
        return None
    except Exception as e:
        print(f"[✘] An unexpected error occurred loading {filepath}: {e}")
        return None

def combine_disaster_data():
    """Combines GDACS and ReliefWeb JSON data into a single file."""
    # Define the base directory relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_json_dir = os.path.join(script_dir, "JSON")
    gdacs_dir = os.path.join(base_json_dir, "gdacs")
    relief_dir = os.path.join(base_json_dir, "relief")
    output_dir = base_json_dir # Save combined file in the JSON directory

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        print(f"[✘] Output directory does not exist: {output_dir}")
        print("[!] Please run the data fetching script first to generate the data.")
        return

    print("[*] Finding latest GDACS and ReliefWeb data files...")

    # Find the latest GDACS file
    latest_gdacs_file = find_latest_json(gdacs_dir, "gdacs_alerts_relevant_")
    if not latest_gdacs_file:
        print("[✘] Could not find the latest GDACS JSON file. Skipping combination.")
        return

    # Find the latest ReliefWeb file
    latest_reliefweb_file = find_latest_json(relief_dir, "reliefweb_disasters_")
    if not latest_reliefweb_file:
        print("[✘] Could not find the latest ReliefWeb JSON file. Skipping combination.")
        return

    print(f"[*] Latest GDACS file found: {latest_gdacs_file}")
    print(f"[*] Latest ReliefWeb file found: {latest_reliefweb_file}")

    # Load the data from the files
    gdacs_data = load_json_file(latest_gdacs_file)
    reliefweb_data = load_json_file(latest_reliefweb_file)

    if gdacs_data is None or reliefweb_data is None:
        print("[✘] Failed to load data from one or both files. Cannot combine.")
        return

    # Combine the data into a single structure
    # Using a dictionary to hold the data from each source
    combined_data = {
        "gdacs_alerts": gdacs_data,
        "reliefweb_disasters": reliefweb_data
    }

    # Generate a timestamp for the combined file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_filename = f"combined_disaster_data_{timestamp}.json"
    combined_filepath = os.path.join(output_dir, combined_filename)

    # Save the combined data to a new JSON file
    try:
        with open(combined_filepath, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=4)
        print(f"[✔] Combined disaster data saved to {combined_filepath}")
    except Exception as e:
        print(f"[✘] Error saving combined data to {combined_filepath}: {e}")

# ========== RUN SCRIPT ==========\n
if __name__ == "__main__":
    print("🔄 Combining GDACS and ReliefWeb data...")
    combine_disaster_data()
    print("\nCombination process complete.")
