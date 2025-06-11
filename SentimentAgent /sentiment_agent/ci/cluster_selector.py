# ci/cluster_selector.py

import json
from datetime import datetime

# Define rules for model-to-cluster mapping
CLUSTER_RULES = {
    "deberta": "adaptive_cluster",
    "gemma": "adaptive_cluster",
    "default": "shared_cluster"
}

def select_cluster(model_type: str) -> str:
    for keyword, cluster in CLUSTER_RULES.items():
        if keyword in model_type.lower():
            return cluster
    return CLUSTER_RULES["default"]

def generate_task_json(model_type: str, input_table: str, output_table: str, project_name: str) -> str:
    cluster_key = select_cluster(model_type)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    job_template = {
        "name": f"{project_name}_batch_inference_{timestamp}",
        "tasks": [
            {
                "task_key": "RunInference",
                "python_task": {
                    "python_file": "dbfs:/FileStore/code/batch_inference.py",
                    "parameters": [
                        "--model-name", model_type,
                        "--input-table", input_table,
                        "--output-temp", "/tmp/output.parquet"
                    ]
                },
                "cluster_key": cluster_key
            },
            {
                "task_key": "WriteOutput",
                "depends_on": [
                    {"task_key": "RunInference"}
                ],
                "notebook_task": {
                    "notebook_path": "/Repos/Team/BatchJobs/Write_To_Snowflake",
                    "base_parameters": {
                        "output_table": output_table
                    }
                },
                "cluster_key": "shared_cluster"
            }
        ],
        "job_clusters": []
    }
    return json.dumps(job_template, indent=2)

# Example usage for debugging only:
if __name__ == "__main__":
    print(generate_task_json("deberta-v3-large", "source_table", "sentiment_output", "SentimentApp"))
