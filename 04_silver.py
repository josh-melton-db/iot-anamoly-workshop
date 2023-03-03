# Databricks notebook source
# MAGIC %md
# MAGIC 
# MAGIC ## Parse/Transform the data from Bronze and load to Silver
# MAGIC 
# MAGIC <img src="https://mcg1stanstor00.blob.core.windows.net/images/iot-anomaly-detection/raw/main/resource/images/04_silver.jpg" width="25%">
# MAGIC 
# MAGIC This notebook will stream new events from the Bronze table, parse/transform them, and load them to a Delta table called "Silver".

# COMMAND ----------

# MAGIC %md
# MAGIC Setup

# COMMAND ----------

dbutils.widgets.text("source_table", "bronze")
dbutils.widgets.text("target_table", "silver")
dbutils.widgets.text("database", "rvp_iot_sa")
checkpoint_path = "/dbfs/tmp/checkpoints"

source_table = getArgument("source_table")
target_table = getArgument("target_table")
database = getArgument("database")
checkpoint_location_target = f"{checkpoint_path}/{target_table}"

#Cleanup Previous Run
dbutils.fs.rm(checkpoint_location_target, recurse = True)
spark.sql(f"drop table if exists {database}.{target_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC Incrementally Read data from Bronze

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, FloatType, IntegerType, StringType

bronze_df = (
  spark.readStream
    .format("delta")
    .table(f"{database}.{source_table}")
)

#Uncomment to view the bronze data
#display(bronze_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Parse/Transform the Bronze data

# COMMAND ----------

#Schema for the Payload column
json_schema = StructType([
  StructField("timestamp", IntegerType(), True),
  StructField("device_id", IntegerType(), True),
  StructField("device_model", StringType(), True),
  StructField("sensor_1", FloatType(), True),
  StructField("sensor_2", FloatType(), True),
  StructField("sensor_3", FloatType(), True),
  StructField("state", StringType(), True)
])

#Parse/Transform
transformed_df = (
  bronze_df
    .withColumn("struct_payload", F.from_json("parsedValue", schema = json_schema)) #Apply schema to payload
    .select("struct_payload.*", F.from_unixtime("struct_payload.timestamp").alias("datetime"))
    .drop('timestamp')
            )

#Uncomment to display the transformed data
#display(transformed_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Write transformed data to Silver

# COMMAND ----------

(
  transformed_df
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_location_target)
    .trigger(once = True) #Comment to continuously stream
    .table(f"{database}.{target_table}")
)

# COMMAND ----------

#Display Silver Table
display(spark.table(f"{database}.{target_table}"))
