from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("smart-office-kafka-smoke-test")
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
        "subscribe",
        "smartoffice.hr.employees",
    )
    .option(
        "startingOffsets",
        "earliest",
    )
    .load()
)


output_df = kafka_df.selectExpr(
    "CAST(key AS STRING) AS kafka_key",
    "CAST(value AS STRING) AS kafka_value",
    "topic",
    "partition",
    "offset",
    "timestamp"
)


query = (
    output_df.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .start()
)


query.awaitTermination()