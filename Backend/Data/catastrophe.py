import requests
import yaml

# Load configuration
with open("Data/config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_conf = config["api"]
query_conf = config["query"]
output_conf = config["output"]

# Build base URL
base_url = f"{api_conf['scheme']}://{api_conf['host']}{api_conf['path']}"

# Build query parameters
params = {
    "appname": api_conf["appname"],
    "limit": query_conf["limit"],
    "profile": query_conf["profile"],
    "sort[]": query_conf.get("sort", [])
}

# Add optional filters
filters = query_conf.get("filters", {})
for key, value in filters.items():
    if value:
        params[f"filter[field][{key}]"] = value

# Request data
response = requests.get(base_url, params=params)

# Display response
if response.status_code == 200:
    data = response.json()
    for disaster in data.get("data", []):
        fields = disaster.get("fields", {})
        if output_conf["fields"]:
            for field in output_conf["fields"]:
                print(f"{field}: {fields.get(field)}")
        else:
            print(fields)
        print("=" * 60)
else:
    print(f"Request failed: {response.status_code}")
