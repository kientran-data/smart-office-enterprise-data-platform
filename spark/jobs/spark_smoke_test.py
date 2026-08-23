from pyspark.sql import SparkSession


spark = (
    SparkSession.builder
    .appName("smart-office-spark-smoke-test")
    .getOrCreate()
)


df = spark.range(1, 11)

df.show()


print(
    "ROW COUNT:",
    df.count(),
)


spark.stop()