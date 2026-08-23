import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import get_json_object

MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]

spark = (
    SparkSession.builder
    .appName("smart-office-validate-bronze")
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
    .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.endpoint.region", "us-east-1")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .getOrCreate()
)

print("\n\n" + "="*50)
print("8.15 — Validate Bronze row")
print("="*50)

df = (
    spark.read
    .parquet("s3a://smart-office-bronze/cdc/")
)

df.printSchema()

# In 5 dòng mẫu thay vì 20 để terminal đỡ bị trôi
df.show(5, truncate=False)

print("\n\n" + "="*50)
print("8.16 — Kiểm tra CDC operations")
print("="*50)

df.select(
    "source_schema",
    "source_table",
    get_json_object("kafka_value", "$.op").alias("op"),
).groupBy(
    "source_schema",
    "source_table",
    "op",
).count().orderBy(
    "source_schema", 
    "source_table"
).show(100, truncate=False)

spark.stop()
