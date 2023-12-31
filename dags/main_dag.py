import os
from airflow import DAG
from datetime import timedelta, datetime
import json
import requests
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from constants import *
import boto3
from dotenv import load_dotenv

# load .env
load_dotenv()

# stop all airflow 
# kill $(ps -ef | grep "airflow scheduler" | awk '{print $2}')
# kill $(ps aux | grep "airflow" | awk '{print $2}')

# init api headers
api_host_key = {"X-RapidAPI-Key": os.getenv("API_KEY"),
                "X-RapidAPI-Host":  os.getenv("API_HOST")}

# To connect to an AWS service
# reference: https://towardsthecloud.com/aws-sdk-aws-credentials-boto3
# reference iam: https://www.youtube.com/watch?v=TlCuOjviOhk
# *IMPORTANT NOTE: an IAM role to access s3 bucket must be created prior to connecting without explicitly putting in your credentials
s3 = boto3.resource('s3')

def extract_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']
    # return headers
    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()


    # Specify the output file path
    filename=f'response_data_{dt_string}'
    output_file_path = f"/home/ubuntu/extract_output/{filename}.json"
    file_str = f'{filename}.csv'

    # Write the JSON response to a file
    with open(output_file_path, "w") as output_file:
        json.dump(response_data, output_file, indent=4)  # indent for pretty formatting

    # Upload files to S3 bucket
    s3.Bucket(S3_EXTRACT_BUCKET).upload_file(Filename=output_file_path, Key=f"{filename}.json")

    return output_file_path, file_str


with DAG('zillow_analytics_dag',
         default_args=DEFAULT_ARGS,
         schedule_interval='@daily',
         catchup=False) as dag:

    extract_zillow_data_task = PythonOperator(
        task_id='extract_zillow_data_task',
        python_callable=extract_zillow_data,
        op_kwargs={
            'url': 'https://zillow56.p.rapidapi.com/search',
            'querystring': {"location": "toronto, canada"},
            'headers': api_host_key,
            'date_string': datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        }
    )

    # this operator ensure that there exists the transformed csv file b4 triggering S3->Redshift Operator
    is_file_in_s3_available_task = S3KeySensor(
        task_id='is_file_in_s3_available_task',
        bucket_key='{{ ti.xcom_pull(task_ids="extract_zillow_data_task")[1] }}',
        bucket_name=S3_TRANSFORMED_BUCKET,
        aws_conn_id='aws_s3_conn',
        wildcard_match=False, # Set to True if you want to use wildcards in the prefix
        timeout=60, # in seconds
        poke_interval=5 # in seconds
    )

    transfer_s3_to_redshift_task = S3ToRedshiftOperator(
        task_id="transfer_s3_to_redshift_task",
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket=S3_TRANSFORMED_BUCKET,
        s3_key='{{ ti.xcom_pull(task_ids="extract_zillow_data_task")[1] }}',
        schema="PUBLIC",
        table="TorontoHousing",
        copy_options=["csv IGNOREHEADER 1"]
    )

    # Setting up the task dependencies
    extract_zillow_data_task >> is_file_in_s3_available_task >> transfer_s3_to_redshift_task