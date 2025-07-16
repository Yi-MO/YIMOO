import requests
from requests.auth import HTTPBasicAuth
import json
import urllib3
import csv
import re
import os  # For directory operations
from datetime import datetime

# Disable SSL certificate warning (only when verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===================== Configuration =====================
OUTPUT_DIR = "output"  # Output directory
ELASTICSEARCH_URL = "https://sr-cnvelk01.ftmcn.cn:9200"  # Elasticsearch address
INDEX = "fmlogs*"                                         # Log index name
USERNAME = "fmsupport"                                       # Username
PASSWORD = "futur_master_2020"                                 # Password
LOG_FILE_JSON = os.path.join(OUTPUT_DIR, "micro_service_dolap_logs.json")  # Raw log output file (JSON)
LOG_FILE_CSV = os.path.join(OUTPUT_DIR, "micro_service_dolap_logs.csv")    # Parsed log output file (CSV)

# ===================== Query Body =====================
# Multi-condition AND search, limited to the past month
query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"environment": "sr-cnvdolap-qa04.ftmcn.cn"}},
                {"term": {"service": "micro-service-dolap"}},
                {"match_phrase": {"message": "[OLAP result]"}},
                {
                    "range": {
                        "@timestamp": {
                            "gte": "now-1M/M",  # Past one month
                            "lte": "now",
                            "time_zone": "+08:00"  # Specify timezone (e.g., +08:00 for China)
                        }
                    }
                }
            ]
        }
    },
    "size": 100  # Number of logs to retrieve
}

# ===================== Utility Function =====================
def parse_message_for_fields(message):
    """
    Extract USER_NAME and KEY fields from the message. Supports formats like user:FM;key=A_DEMO_02
    """
    result = {"USER_NAME": "", "KEY": ""}
    # Match user:xxx or user=xxx, stop at semicolon, space, parenthesis, etc.
    user_match = re.search(r'user[:=]([^\s；;，,\)\(]+)', message, re.IGNORECASE)
    key_match = re.search(r'key[:=]([^\s；;，,\)\(]+)', message, re.IGNORECASE)
    if user_match:
        result["USER_NAME"] = user_match.group(1)
    if key_match:
        result["KEY"] = key_match.group(1)
    return result

# ===================== Main Process =====================
def fetch_logs():
    """
    Fetch logs from Elasticsearch, extract USER_NAME, DATE, and KEY, and output to CSV.
    """
    # Create output directory if it does not exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    url = f"{ELASTICSEARCH_URL}/{INDEX}/_search"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps(query),
        verify=False
    )
    if response.status_code == 200:
        logs = response.json()
        # Save raw logs to JSON file
        with open(LOG_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        print(f"Raw logs saved to {LOG_FILE_JSON}")
        hits = logs.get("hits", {}).get("hits", [])
        rows = []
        for hit in hits:
            source = hit.get("_source", {})
            message = source.get("message", "")
            timestamp = source.get("@timestamp", "")
            # Parse message
            fields = parse_message_for_fields(message)
            # Parse date
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime("%d/%m/%Y")
                except Exception:
                    date_str = ""
            else:
                date_str = ""
            # Assemble a row
            row = {
                "USER_NAME": fields.get("USER_NAME", ""),
                "DATE": date_str,
                "KEY": fields.get("KEY", "")
            }
            rows.append(row)
        # Sort by DATE in ascending order (empty dates at the end)
        def date_key(row):
            try:
                return datetime.strptime(row["DATE"], "%d/%m/%Y") if row["DATE"] else datetime.max
            except Exception:
                return datetime.max
        rows.sort(key=date_key)
        # Write to CSV with semicolon as delimiter
        with open(LOG_FILE_CSV, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["USER_NAME", "DATE", "KEY"], delimiter=';')
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Extracted USER_NAME, DATE, KEY and saved to {LOG_FILE_CSV}")
    else:
        print(f"Failed to fetch logs, status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_logs()