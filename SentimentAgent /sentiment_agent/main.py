# sentiment_agent/main.py

import argparse
from sentiment_agent.core.utils import create_spark_session
from sentiment_agent.core.data_loader import load_from_csv, load_from_snowflake, validate_text_column
from sentiment_agent.core.inference import run_inference
from sentiment_agent.core.writer import write_to_snowflake
from sentiment_agent.core.finetune import run_finetuning


def main():
    parser = argparse.ArgumentParser(description="Sentiment Analysis Agent")
    parser.add_argument("--task", choices=["inference", "finetune"], required=True)
    parser.add_argument("--model", choices=["nli", "gemma"], required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--text_col", default="text")

    # For inference
    parser.add_argument("--input_csv", help="Path to input CSV")
    parser.add_argument("--output_csv", help="Optional path to save results")

    # For Snowflake batch
    parser.add_argument("--snowflake", action="store_true")
    parser.add_argument("--sf_config", help="Path to Snowflake config JSON")
    parser.add_argument("--sf_output_table", help="Snowflake output table name")

    # For finetuning
    parser.add_argument("--train_csv", help="Path to labeled training CSV")

    args = parser.parse_args()
    spark = create_spark_session()

    model_config = {"model_name": "MoritzLaurer/deberta-v3-large-zeroshot-v2.0" if args.model == "nli" else "google/gemma-2b"}

    if args.task == "finetune":
        if not args.train_csv:
            raise ValueError("Training CSV must be provided for fine-tuning.")
        run_finetuning(
            csv_path=args.train_csv,
            model_type=args.model,
            project=args.project,
            model_config=model_config
        )

    elif args.task == "inference":
        if args.snowflake:
            import json
            with open(args.sf_config, "r") as f:
                sf_conf = json.load(f)
            df = load_from_snowflake(spark, sf_conf)
            validate_text_column(df, args.text_col)
            df_result = run_inference(spark, df, args.text_col, args.model, model_config)
            write_to_snowflake(df_result, spark, sf_conf, args.sf_output_table)
        else:
            df = load_from_csv(spark, args.input_csv)
            validate_text_column(df, args.text_col)
            df_result = run_inference(spark, df, args.text_col, args.model, model_config)
            if args.output_csv:
                df_result.toPandas().to_csv(args.output_csv, index=False)
                print(f"Results saved to {args.output_csv}")
            else:
                df_result.show()


if __name__ == "__main__":
    main()

