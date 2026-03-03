from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
import time

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("DeltaCDCReader") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Path to your Delta table
delta_table_path = "/opt/spark/delta/cdc_writer_table"

# Define schema
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("timestamp", TimestampType(), True)
])

# Check if table exists, if not create it first
try:
    spark.read.format("delta").load(delta_table_path)
except Exception as e:
    print(f"Delta table not found or unreadable: {e}")
    print("Please run the writer script first to create the table with CDC enabled.")
    exit(1)

print("Delta table exists, proceeding with CDC reading...")


def run_cdc_stream(checkpoint_location):
    cdc_df = spark.readStream \
        .format("delta") \
        .option("readChangeFeed", "true") \
        .load(delta_table_path)

    windowed_df = cdc_df \
        .groupBy(
            window(col("_commit_timestamp"), "10 seconds"),
            col("_change_type")
        ) \
        .count() \
        .selectExpr(
            "window.start as window_start",
            "window.end as window_end",
            "_change_type as change_type",
            "count"
        )

    query = windowed_df.writeStream \
        .format("console") \
        .outputMode("complete") \
        .option("checkpointLocation", checkpoint_location) \
        .trigger(processingTime="10 seconds") \
        .start()

    query.awaitTermination(60)
    if query.isActive:
        query.stop()


try:
    checkpoint_path = f"/tmp/delta-cdc-checkpoint-{int(time.time())}"
    try:
        run_cdc_stream(checkpoint_path)
    except Exception as first_error:
        retry_checkpoint = f"/tmp/delta-cdc-checkpoint-retry-{int(time.time())}"
        print(
            "Detected checkpoint/offset startup issue. "
            f"Retrying once with fresh checkpoint: {retry_checkpoint}"
        )
        run_cdc_stream(retry_checkpoint)
except Exception as e:
    print(f"Error reading Delta table: {e}")
    exit(1)