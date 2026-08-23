import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    split,
    to_date,
)

MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]

spark = (
    SparkSession.builder
    .appName(
        "smart-office-bronze-cdc"
    )
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        "http://minio:9000",
    )
    .config(
        "spark.hadoop.fs.s3a.access.key",
        MINIO_ACCESS_KEY,
    )
    .config(
        "spark.hadoop.fs.s3a.secret.key",
        MINIO_SECRET_KEY,
    )
    .config(
        "spark.hadoop.fs.s3a.path.style.access",
        "true",
    )
    .config(
        "spark.hadoop.fs.s3a.connection.ssl.enabled",
        "false",
    )
    .config(
        "spark.hadoop.fs.s3a.endpoint.region",
        "us-east-1",
    )
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )
    .getOrCreate()
)

kafka_df = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "kafka:19092",
    )
    .option(
        "subscribePattern",
        r"smartoffice\."
        r"(hr|office|access|meeting|signing|iot)"
        r"\..*",
    )
    .option(
        "startingOffsets",
        "earliest",
    )
    .option(
        "failOnDataLoss",
        "true",
    )
    .load()
)

bronze_df = (
    kafka_df
    .select(
        col("key")
        .cast("string")
        .alias("kafka_key"),
        col("value")
        .cast("string")
        .alias("kafka_value"),
        col("topic")
        .alias("kafka_topic"),
        col("partition")
        .alias("kafka_partition"),
        col("offset")
        .alias("kafka_offset"),
        col("timestamp")
        .alias("kafka_timestamp"),
    )
    .withColumn(
        "source_schema",
        split(
            col("kafka_topic"),
            r"\.",
        ).getItem(1),
    )
    .withColumn(
        "source_table",
        split(
            col("kafka_topic"),
            r"\.",
        ).getItem(2),
    )
    .withColumn(
        "ingested_at",
        current_timestamp(),
    )
    .withColumn(
        "ingest_date",
        to_date(
            col("ingested_at")
        ),
    )
)

query = (
    bronze_df.writeStream
    .format("parquet")
    .outputMode("append")
    .option(
        "path",
        "s3a://smart-office-bronze/cdc/",
    )
    .option(
        "checkpointLocation",
        "s3a://smart-office-checkpoints/bronze-cdc/",
    )
    .partitionBy(
        "source_schema",
        "source_table",
        "ingest_date",
    )
    .trigger(
        processingTime="10 seconds"
    )
    .start()
)

query.awaitTermination()