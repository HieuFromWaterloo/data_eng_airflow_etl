# Data Engineering with Airflow ETL

The goal of this ETL pipeline is to connect to the OpenWeatherMap API, retrieve weather data, process it, and store it in an Amazon S3 bucket. Apache Airflow is used to manage the workflow, making it easy to automate and schedule tasks.

## Prerequisites

Before you start, make sure you have the following prerequisites in place:

- An AWS account with an EC2 instance running Ubuntu.
- Python, pip, and virtualenv installed on your EC2 instance.
- Additional Python packages like pandas and S3FS installed.
- Apache Airflow installed on your EC2 instance.

## Setting Up AWS EC2 Instance

1. Create an AWS EC2 instance with Ubuntu.
2. Choose an appropriate instance type and create a key pair.
3. Update the security group rules to allow access to port 8080 for Apache Airflow's UI.

## Installing Dependencies

1. Connect to your EC2 instance.
2. Install necessary dependencies like Python, pip, and virtualenv.
3. Create a virtual environment for your project and activate it using `source venv_name/bin/activate`.
4. Install additional Python packages like pandas and S3FS.

## Setting Up Apache Airflow

1. Install Apache Airflow on your EC2 instance using `sudo pip install apache-airflow`.
2. Configure and initialize Apache Airflow.
3. Access the Airflow web server via a web interface on your EC2 instance to configure and manage your data pipelines.

## Creating and Managing DAGs

1. Understand Directed Acyclic Graphs (DAGs) in Apache Airflow.
2. Create a DAG and define its parameters, including start date, schedule interval, and catch-up behavior.
3. Ensure the OpenWeatherMap API is available before proceeding with data extraction by creating a task within the DAG.

## Data Extraction

1. Create a task in Apache Airflow to connect to the API using an HTTP sensor.
2. Use an HTTP sensor to wait for a specific condition to be met before moving to the next task.
3. Create a task to extract data using a SimpleHttpOperator in Airflow.

## Data Transformation

1. Use a PythonOperator in Airflow to run a Python function for data transformation.
2. Perform data transformation using libraries like Pandas.
3. Utilize `task_instance.xcom_pull` to retrieve data from a previous task in the workflow.
4. Perform data transformations such as unit conversions and time zone adjustments.

## Loading Data to AWS S3

1. Define task dependencies in Apache Airflow to specify the order in which tasks should run.
2. Save the output files generated in the ETL pipeline to an S3 bucket in AWS.
3. Create an AWS access key and configure the AWS CLI on the EC2 instance.
4. Provide AWS credentials as a dictionary to the `pandas.to_csv` storage options to save data in an S3 bucket.

## Monitoring and Maintenance

1. Monitor the Airflow UI for task execution and status.
2. Refresh the UI to ensure updates propagate and tasks run successfully.

## Future Enhancements

This project serves as a foundation for more advanced data workflows. Future enhancements can include designing workflows with parallel tasks that merge at certain points in the process.
