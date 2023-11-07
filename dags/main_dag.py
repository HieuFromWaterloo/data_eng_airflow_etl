from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor
import json
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd
from constants import *

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
    aws_credentials = {"key": "xxxxxxxxx", "secret": "xxxxxxxxxx", "token": "xxxxxxxxxxxxxx"}

    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = f'current_weather_data_toronto_{dt_string}'
    df_data.to_csv(f"s3://weatherapiairflowyoutubebucket-yml/{dt_string}.csv", index=False, storage_options=aws_credentials)


with DAG('weather_dag',
        default_args=default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:


        is_weather_api_ready = HttpSensor(
            task_id ='is_weather_api_ready',
            http_conn_id='weathermap_api',
            endpoint='/data/2.5/weather?q=Toronto&APPID=5031cde3d1a8b9469fd47e998d7aef79'
        )


        extract_weather_data = SimpleHttpOperator(
            task_id = 'extract_weather_data',
            http_conn_id = 'weathermap_api',
            endpoint='/data/2.5/weather?q=Toronto&APPID=5031cde3d1a8b9469fd47e998d7aef79',
            method = 'GET',
            response_filter= lambda r: json.loads(r.text),
            log_response=True
        )

        transform_load_weather_data = PythonOperator(
            task_id= 'transform_load_weather_data',
            python_callable=transform_load_data
        )

        is_weather_api_ready >> extract_weather_data >> transform_load_weather_data
