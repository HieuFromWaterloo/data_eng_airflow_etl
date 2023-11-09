from datetime import datetime, timedelta

S3_EXTRACT_BUCKET='s3e-bucket'
S3_LOAD_BUCKET='s3l-bucket'
S3_TRANSFORMED_BUCKET='s3t-bucket'

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