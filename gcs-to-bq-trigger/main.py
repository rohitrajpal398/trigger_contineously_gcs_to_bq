import base64
import json
from flask import Flask, request
from google.cloud import bigquery

app = Flask(__name__)
bq_client = bigquery.Client()

# Set your BQ config
DATASET = "sales_dataset"
TABLE = "orders.csv"
PROJECT = "airy-actor-457907-a8."

@app.route("/", methods=["POST"])
def gcs_event():
    envelope = request.get_json()
    
    if not envelope or 'message' not in envelope:
        return "No message", 400
    
    msg = envelope['message']
    if 'data' in msg:
        payload = base64.b64decode(msg['data']).decode('utf-8')
        attrs = json.loads(payload)
        file_name = attrs['name']
        bucket = attrs['bucket']

        uri = f"gs://{bucket}/{file_name}"
        print(f"Loading file: {uri}")

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            autodetect=True,  # change if you have schema
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        load_job = bq_client.load_table_from_uri(
            uri,
            f"{PROJECT}.{DATASET}.{TABLE}",
            job_config=job_config
        )
        load_job.result()
        return f"File {file_name} loaded to BQ", 200

    return "No data in message", 400
