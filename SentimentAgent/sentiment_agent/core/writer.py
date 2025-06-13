# sentiment_agent/core/writer.py

def write_to_snowflake(df, spark, sf_config: dict, output_table: str):
    required_keys = ["sfURL", "sfUser", "sfPassword", "sfDatabase", "sfSchema", "sfWarehouse"]
    for k in required_keys:
        if k not in sf_config:
            raise ValueError(f"Missing Snowflake config key: {k}")

    sf_options = sf_config.copy()
    sf_options["dbtable"] = output_table

    df.write \
        .format("snowflake") \
        .options(**sf_options) \
        .mode("overwrite") \
        .save()
