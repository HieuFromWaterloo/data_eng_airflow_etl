import os
from airflow import DAG
from datetime import datetime
from airflow.providers.http.sensors.http import HttpSensor
import json
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd
from constants import *
import boto3
from dotenv import load_dotenv

# To connect to an AWS service
# reference: https://towardsthecloud.com/aws-sdk-aws-credentials-boto3
# reference iam: https://www.youtube.com/watch?v=TlCuOjviOhk
# *IMPORTANT NOTE: an IAM role to access s3 bucket must be created prior to connecting without explicitly putting in your credentials
s3 = boto3.resource('s3')

# load .env
load_dotenv()
# init endpoint api key
endpoint_key = os.getenv("DATA_API_KEY")

def kelvin_to_celcius(temp_in_kelvin):
    return (temp_in_kelvin - 273.15)


def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_farenheit = kelvin_to_celcius(data["main"]["temp"])
    feels_like_farenheit= kelvin_to_celcius(data["main"]["feels_like"])
    min_temp_farenheit = kelvin_to_celcius(data["main"]["temp_min"])
    max_temp_farenheit = kelvin_to_celcius(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {"City": city,
                        "Description": weather_description,
                        "Temperature (F)": temp_farenheit,
                        "Feels Like (F)": feels_like_farenheit,
                        "Minimun Temp (F)":min_temp_farenheit,
                        "Maximum Temp (F)": max_temp_farenheit,
                        "Pressure": pressure,
                        "Humidty": humidity,
                        "Wind Speed": wind_speed,
                        "Time of Record": time_of_record,
                        "Sunrise (Local Time)":sunrise_time,
                        "Sunset (Local Time)": sunset_time                        
                        }
    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)

    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = f'current_weather_data_toronto_{dt_string}'
    df_data.to_csv(f"{dt_string}.csv", sep=',', index=False)

    # Upload files to S3 bucket
    # the key param is to indicate the filename that you want it to be saved in s3
    # e.g. equivant cli: aws s3 cp Filename s3://<s3_bucket_name>/Key
    s3.Bucket('s3-cua-tao').upload_file(Filename=f"{dt_string}.csv", Key=f"{dt_string}.csv")


with DAG('weather_dag',
        default_args=default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:


        is_weather_api_ready = HttpSensor(
            task_id ='is_weather_api_ready',
            http_conn_id='weathermap_api',
            endpoint=f'/data/2.5/weather?q=Toronto&APPID={endpoint_key}'
        )


        extract_weather_data = SimpleHttpOperator(
            task_id = 'extract_weather_data',
            http_conn_id = 'weathermap_api',
            endpoint=f'/data/2.5/weather?q=Toronto&APPID={endpoint_key}',
            method = 'GET',
            response_filter= lambda r: json.loads(r.text),
            log_response=True
        )

        transform_load_weather_data = PythonOperator(
            task_id= 'transform_load_weather_data',
            python_callable=transform_load_data
        )

        is_weather_api_ready >> extract_weather_data >> transform_load_weather_data
