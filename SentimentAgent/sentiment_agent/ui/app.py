# sentiment_agent/ui/app.py

import streamlit as st
from sentiment_agent.core.utils import setup_logger, suggest_resolution, get_timestamped_filename
from sentiment_agent.core.inference import run_inference
from sentiment_agent.core.data_loader import load_from_csv, load_from_snowflake, validate_text_column
from sentiment_agent.core.finetune import run_finetuning
from sentiment_agent.core.writer import write_to_snowflake
from sentiment_agent.core.utils import create_spark_session
import tempfile

setup_logger()
spark = create_spark_session()

st.set_page_config(page_title="Sentiment Analysis Agent", layout="wide")
st.title("🧠 Sentiment Analysis Agent")

# Sidebar Configuration
with st.sidebar:
    st.header("🛠️ Configuration")
    project = st.text_input("Project Name", help="Used for MLflow and tracking.")
    model_type = st.selectbox("Select Model", ["nli", "gemma"], help="Choose the sentiment model.")
    task = st.radio("Task", ["Inference", "Fine-Tuning"], help="Select your task.")

    if task == "Fine-Tuning":
        label_file = st.file_uploader("Labeled CSV ('text' & 'label')", type="csv")

    else:
        datasource = st.radio("Data Source", ["CSV", "Snowflake"])
        if datasource == "CSV":
            infer_file = st.file_uploader("Inference CSV", type="csv")
        else:
            sf_config = {
                "sfURL": st.text_input("Snowflake URL"),
                "sfUser": st.text_input("Username"),
                "sfPassword": st.text_input("Password", type="password"),
                "sfDatabase": st.text_input("Database"),
                "sfSchema": st.text_input("Schema"),
                "sfWarehouse": st.text_input("Warehouse"),
                "dbtable": st.text_input("Input Table Name"),
            }
            sf_output = st.text_input("Output Table Name")

    text_col = st.text_input("Text Column", value="text")
    run_button = st.button("🚀 Execute")

if run_button and project and model_type and text_col:
    try:
        model_config = {"model_name": "MoritzLaurer/deberta-v3-large-zeroshot-v2.0" if model_type == "nli" else "google/gemma-2b"}

        if task == "Fine-Tuning":
            if not label_file:
                st.warning("Upload a labeled CSV file to continue.")
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                    tmp.write(label_file.getbuffer())
                    tmp_path = tmp.name

                version = run_finetuning(tmp_path, model_type, project, model_config)
                st.success(f"Fine-tuned model registered: {version}")

        else:
            if datasource == "CSV":
                if not infer_file:
                    st.warning("Upload a CSV file for inference.")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                        tmp.write(infer_file.getbuffer())
                        tmp_path = tmp.name

                    df = load_from_csv(spark, tmp_path)
                    validate_text_column(df, text_col)
                    df_result = run_inference(spark, df, text_col, model_type, model_config)
                    csv_name = get_timestamped_filename(f"{project}_results")
                    df_result.toPandas().to_csv(csv_name, index=False)
                    st.success("Inference complete!")
                    st.download_button("📥 Download Results", data=open(csv_name, "rb"), file_name=csv_name)

            else:
                df = load_from_snowflake(spark, sf_config)
                validate_text_column(df, text_col)
                df_result = run_inference(spark, df, text_col, model_type, model_config)
                st.info("Writing results to Snowflake...")
                write_to_snowflake(df_result, spark, sf_config, sf_output)
                st.success(f"Results written to Snowflake: {sf_output}")

    except Exception as e:
        st.error(f"Error encountered: {e}")
        st.info(suggest_resolution(e))
