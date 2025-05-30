## How to create worflow through job_config json 

### Step 1: Export the Workflow Configuration

1. **Use the Databricks REST API**: You can use the Databricks REST API to export the configuration of an existing job. The endpoint you would use is `/jobs/get`. You will need the job ID of the workflow you want to export.

   Here’s an example of how to get the job configuration using `curl`:

   ```bash
   curl -X GET \
     -H "Authorization: Bearer <your_token>" \
     "https://<your_databricks_instance>/api/2.0/jobs/get?job_id=<job_id>"
   ```

   Replace `<your_token>`, `<your_databricks_instance>`, and `<job_id>` with your actual Databricks token, instance URL, and job ID.

2. **Save the JSON Response**: The response will contain the job configuration in JSON format. Save this response to a file (e.g., `job_config.json`).

### Step 2: Modify the JSON Configuration

1. **Edit the JSON File**: Open the downloaded `job_config.json` file in a text editor. Look for the sections that specify the paths of the notebooks you want to change. Update the paths as needed.

### Step 3: Create a New Workflow

1. **Use the Databricks REST API**: After modifying the JSON file, you can create a new job using the `/jobs/create` endpoint. You will need to modify the JSON slightly to ensure it is valid for creating a new job (e.g., removing the job ID, if present).

   Here’s an example of how to create a new job using `curl`:

   ```bash
   curl -X POST \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d @job_config_modified.json \
     "https://<your_databricks_instance>/api/2.0/jobs/create"
   ```

   Make sure to replace `<your_token>`, `<your_databricks_instance>`, and `job_config_modified.json` with your actual Databricks token, instance URL, and the path to your modified job configuration file.

### Additional Notes

- **Permissions**: Ensure that you have the necessary permissions to access the job and create new jobs in your Databricks workspace.
- **API Documentation**: Refer to the [Databricks API documentation](https://docs.databricks.com/dev-tools/api/latest/index.html) for more details on the endpoints and the expected JSON structure.
- **Testing**: After creating the new workflow, test it to ensure that it runs as expected with the updated notebook paths.

By following these steps, you should be able to successfully change the paths of the notebooks in your Databricks workflow.