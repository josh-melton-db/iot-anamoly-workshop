# Databricks notebook source
# MAGIC %md 
# MAGIC %md 
# MAGIC # Real-time Monitoring and Anomaly Detection on Streaming IoT pipelines in Manufacturing 
# MAGIC 
# MAGIC Manufacturers today face challenges working with IoT data due to high investment costs, security, and connectivity outages. These challenges lead to more time and money being spent on trying to make things work rather than innovating on data products that drive business value.  The Databricks Lakehouse platform reduces these challenges with a reliable, secure platform capable of ingesting and transforming IoT data at massive scale, building analytics and AI assets on that data, and serving those assets where they are needed
# MAGIC 
# MAGIC In this solution accelerator, we show how to build a streaming pipeline for IoT data, train a machine learning model on that data, and use that model to make predictions on new IoT data.
# MAGIC 
# MAGIC The pattern shown consumes data from an Apache Kafka stream. Kafka is a distributed event streaming message bus that combines the best features of queuing and publish-subscribe technologies. [Kafka connectors for Spark\\({^T}{^M}\\) Structured Streaming](https://docs.databricks.com/structured-streaming/kafka.html) are packaged together within the Databricks runtime, making it easy to get started. Using these connectors, data from Kafka streams can easily be persisted into Delta Lakehouse. From there, advanced analytics or machine learning algorithms may be executed on the data.
# MAGIC 
# MAGIC You may find this series of notebooks at https://github.com/databricks-industry-solutions/iot-anomaly-detection. 
# MAGIC 
# MAGIC <p></p>
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/iot-anomaly-detection/blob/main/images/iot_streaming_lakehouse.png?raw=true" width=75%/>
# MAGIC 
# MAGIC <p></p>
# MAGIC 
# MAGIC ## Stream the Data from Kafka into a Bronze Delta Table
# MAGIC 
# MAGIC <p></p>
# MAGIC <center><img src="https://github.com/databricks-industry-solutions/iot-anomaly-detection/blob/main/images/03_bronze.jpg?raw=true" width="30%"></center>
# MAGIC 
# MAGIC 
# MAGIC This notebook will read iot data from a location in dbfs and put it into a Delta Lake table called "bronze_iot_anomaly" - for more detail on streaming from kafka see here JOSH TODO: INSERT LINK TO KAFKA DOCS

# COMMAND ----------

# DBTITLE 1,Define configs that are consistent throughout the accelerator
# MAGIC %run ./util/notebook-config $reset_all_data=true

# COMMAND ----------

# DBTITLE 1,Define config for this notebook 
# define target table for this notebook
target_table = bronze
checkpoint_location_target = f"{checkpoint_path}/{target_table}"

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC ### Write the streaming source data to Bronze Delta table
# MAGIC 
# MAGIC Here we generate some data and pump the data into the source location. For your use case, if there is a Kafka topic with data continuously arriving, you can skip the following data generation step.

# COMMAND ----------

# MAGIC %run ./util/generate-iot-data

# COMMAND ----------

# MAGIC %md
# MAGIC JOSH TODO DESCRIPTION

# COMMAND ----------

read_raw = (
  spark.readStream.format('cloudFiles')
  .option("cloudFiles.format", "json")
  .schema(df.schema) # JOSH TODO: DEFINE SCHEMA EXPLICITLY
  .load(raw_path)
  .writeStream.format("delta")
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .toTable(f"{database}.{target_table}")
  .awaitTermination()
)

# COMMAND ----------

#Display records from the Bronze table
display(
spark.table(f"{database}.{target_table}")
)

# COMMAND ----------


