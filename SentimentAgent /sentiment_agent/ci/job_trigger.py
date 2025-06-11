# ci/job_trigger.py

import requests
import json
import os
from ci.cluster_selector import generate_task_json

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

def trigger_job(model_type: str, input_table: str, output_table: str, project_name: str):
    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN]):
        raise EnvironmentError("DATABRICKS_HOST and DATABRICKS_TOKEN must be set as environment variables.")

    payload = generate_task_json(
        model_type=model_type,
        input_table=input_table,
        output_table=output_table,
        project_name=project_name
    )

    url = f"{DATABRICKS_HOST}/api/2.1/jobs/create"
    response = requests.post(url, headers=HEADERS, data=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to trigger Databricks job: {response.status_code} - {response.text}")

    print("✅ Job submitted successfully. Job ID:", response.json().get("job_id"))


# Example usage (for testing only):
if __name__ == "__main__":
    trigger_job(
        model_type="deberta-v3-large",
        input_table="RAW_DB.CALL_TRANSCRIPTS",
        output_table="CURATED_DB.SENTIMENT_RESULTS",
        project_name="SentimentAgent"
    )
