Absolutely! Here’s a concise **Getting Started Guide** for your sentiment analysis agent, tailored to Databricks, VSCode, and your staged rollout (non-Docker → Docker).

---

# 🏁 Getting Started: Sentiment Analysis Agent

## 1. **Clone the Repository**

```bash
git clone https://your-repo-url/sentiment-agent.git
cd sentiment-agent
```

---

## 2. **Set Up Your Python Environment**

* Ensure Python **3.10** is installed.
* (Recommended) Create a virtual environment:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

---

## 3. **Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. **Configure Required Secrets and Environment Variables**

* **MLflow:** Set your tracking URI or use the Databricks default.
* **Snowflake:** For any feature using Snowflake, ensure you have credentials handy.
* **Example:** Edit or create a `.env` file in the project root:

  ```env
  # .env
  MLFLOW_TRACKING_URI=databricks
  SNOWFLAKE_USER=your_user
  SNOWFLAKE_PASSWORD=your_password
  SNOWFLAKE_ACCOUNT=your_account
  ```
* You may also use VSCode’s built-in environment variable manager or Databricks Secrets for sensitive information.

---

## 5. **Configuration Files**

* **Edit any configuration in `config/`** (e.g., `model_defaults.yaml`) to set default model, batch size, etc.
* **For Snowflake jobs:** Edit your connection details in the UI or in the configuration script, not directly in code.

---

## 6. **Component-wise Testing**

### **A. Data Loading**

Test CSV data load:

```python
from sentiment_agent.core.data_loader import load_from_csv
from sentiment_agent.core.utils import create_spark_session

spark = create_spark_session()
df = load_from_csv(spark, "path/to/sample.csv")
df.show()
```

Test Snowflake data load (ensure config dict is filled):

```python
from sentiment_agent.core.data_loader import load_from_snowflake

sf_config = {
    "sfURL": "...",
    "sfUser": "...",
    "sfPassword": "...",
    "sfDatabase": "...",
    "sfSchema": "...",
    "sfWarehouse": "...",
    "dbtable": "YOUR_TABLE"
}
df = load_from_snowflake(spark, sf_config)
df.show()
```

---

### **B. Model Inference**

Test with a Pandas/Spark DataFrame:

```python
from sentiment_agent.core.inference import run_inference

result_df = run_inference(
    spark,
    df,
    text_col="text",
    model_type="nli",  # or "gemma"
    model_config={"model_name": "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"}
)
result_df.show()
```

---

### **C. Model Fine-Tuning (if applicable)**

```python
from sentiment_agent.core.finetune import run_finetuning

version = run_finetuning(
    csv_path="path/to/labeled_train.csv",
    model_type="nli",
    project="your_project_name",
    model_config={"model_name": "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"}
)
print("Model registered/versioned:", version)
```

---

### **D. UI Testing (Streamlit)**

Launch the UI locally:

```bash
streamlit run sentiment_agent/ui/app.py
```

* Access via [http://localhost:8501](http://localhost:8501)
* Use sidebar to upload files, connect to Snowflake, or run inference/fine-tune.

---

## 7. **End-to-End Run via CLI (Optional)**

```bash
python -m sentiment_agent.main --task inference --model nli --project myproj --input_csv path/to/input.csv --output_csv results.csv --text_col text
```

---

## 8. **Transition to Docker (Later)**

* Build the image:

  ```bash
  docker build -t sentiment-agent:latest .
  ```
* Run the container:

  ```bash
  docker run -p 8501:8501 --env-file .env sentiment-agent:latest
  ```

---

## 9. **Deploy/Run on Databricks**

* Push your image to your registry.
* Reference the Docker image in Databricks job/cluster config as shown in previous instructions.

---

## 10. **Where to Make Changes**

* **Models or configs:** Edit in `config/` or in the Streamlit UI.
* **Cluster/job orchestration:** Use/modify the scripts in `ci/`.
* **Secrets:** Set via Databricks Secrets, `.env`, or environment variable manager.
* **Component tests:** Use VSCode interactive Python or notebooks for exploratory runs.

---

## 11. **Documentation**

* Build API docs:

  ```bash
  cd docs
  make html
  ```
* Open `docs/_build/html/index.html` in your browser.

---

**You’re now ready to experiment, test, and extend your sentiment analysis agent with full control! 🚀**
Let me know if you need walk-throughs for any component or have setup issues.
