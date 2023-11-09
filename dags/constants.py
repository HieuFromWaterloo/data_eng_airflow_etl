from datetime import datetime, timedelta

S3_EXTRACT_BUCKET='s3://s3-cua-tao/data_eng_etl/zillow/extract_output'
S3_LOAD_BUCKET='s3://s3-cua-tao/data_eng_etl/zillow/load_output'
S3_TRANSFORMED_BUCKET='s3://s3-cua-tao/data_eng_etl/zillow/transformed_output'

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 8),
    'email': [],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15)
}