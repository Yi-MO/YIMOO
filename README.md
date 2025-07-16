# Elasticsearch Log Extraction and Analysis Script

## Script Purpose

This script is used to batch fetch log data from Elasticsearch (Kibana supported) based on specified conditions, automatically extract `USER_NAME` and `KEY` information from the log message field, as well as the log time (formatted as DD/MM/YYYY), and output the result as a semicolon-separated CSV file. At the same time, the original log data will also be fully saved as a JSON file for further analysis.

## Main Features
- Supports Elasticsearch basic authentication and HTTPS access
- Supports multi-condition (environment, service, log content, time range) search
- Automatically extracts user and key information from the message field
- Automatically extracts and formats log time
- Outputs raw logs as a JSON file
- Outputs structured logs as a semicolon-separated CSV file, sorted by date in ascending order

## Environment Requirements
- Python 3.7 or above
- requests

Install dependencies:
```bash
pip install requests
```

## Configuration
At the top of `src/main.py`, you can configure the following parameters:
- `ELASTICSEARCH_URL`: Elasticsearch service address
  - Test environment example: `https://sr-cnvelk01.ftmcn.cn:9200`
  - **Production environment example**: `https://ftmr-elk01-0102.fmapp.cloud:9200`
  - If others need to use the production environment, please change `ELASTICSEARCH_URL` to the production address.
- `INDEX`: Log index name (e.g., `fmlogs*`)
- `USERNAME`, `PASSWORD`: Elasticsearch account and password
- `OUTPUT_DIR`: Output file directory (default is `output`)

## Query Condition (`query`) Explanation
The `query` variable in the script is used to set log search conditions, structured as follows:

```python
query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"environment": "sr-cnvdolap-qa04.ftmcn.cn"}},  # Environment variable, modify as needed
                {"term": {"service": "micro-service-dolap"}},             # Service name, modify as needed
                {"match_phrase": {"message": "[OLAP result]"}},           # Log content keyword, modify as needed
                {
                    "range": {
                        "@timestamp": {
                            "gte": "now-1M/M",  # Start time, one month before now
                            "lte": "now",        # End time, now
                            "time_zone": "+08:00" # Timezone (e.g., +08:00 for China)
                        }
                    }
                }
            ]
        }
    },
    "size": 100  # Number of logs to retrieve, adjust as needed
}
```

- **environment**: Specifies the environment the log belongs to (e.g., test, production), modify as needed.
- **service**: Specifies the service name, must match the actual service in the logs.
- **message**: Specifies the keyword or phrase in the log content, adjust as needed.
- **@timestamp**: Specifies the time range, supports relative time (e.g., `now-1M/M` means the past month).
- **size**: Number of logs returned per query, default is 100, adjust as needed.

To search for different environments, services, or content, simply modify the corresponding `term` or `match_phrase` condition.

## Usage
1. **Run the script**
   ```bash
   python src/main.py
   ```
2. **Main steps of the script**
   - Connect to Elasticsearch and search logs according to the set conditions (environment, service, message content, time range, etc.)
   - Get the original log data and save it completely as `output/micro_service_dolap_logs.json`
   - Parse the message field of each log, extract `USER_NAME` and `KEY` (supports formats like `user:xxx`, `key=xxx`, etc.)
   - Extract the `@timestamp` field of the log and format it as `DD/MM/YYYY`
   - Generate a structured CSV file `output/micro_service_dolap_logs.csv`, semicolon-separated, sorted by date in ascending order

## Output Description
- `output/micro_service_dolap_logs.json`: Original log data for further analysis
- `output/micro_service_dolap_logs.csv`: Structured log data with three columns:
  - `USER_NAME`: Username extracted from the message field
  - `DATE`: Log time (DD/MM/YYYY)
  - `KEY`: Key extracted from the message field

## Notes
- The script ignores SSL certificate verification by default (for secure access, you can configure a CA certificate)
- The log message format must contain `user:xxx` or `user=xxx`, `key:xxx` or `key=xxx`
- To adjust search conditions, output fields, or format, please modify the relevant parts in `src/main.py`

---
For more customization needs or if you encounter any problems, feel free to contact!