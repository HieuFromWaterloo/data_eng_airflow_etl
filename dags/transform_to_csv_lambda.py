import boto3
import json
import pandas as pd

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract the source bucket name and object key from the Lambda event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Define the target bucket and the target file name (removing the '.json' extension)
    target_bucket = 'ENTER_S3_TRANSFORMED_BUCKET_HERE'
    target_file_name = object_key.replace('.json', '')
    
    # Wait for the source object to exist before attempting to read
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    
    # Get the object from the source bucket
    response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
    data = response['Body'].read().decode('utf-8')
    
    # Load data into a DataFrame
    df = pd.DataFrame(json.loads(data)["results"])
    
    # Select specific columns for the DataFrame
    selected_columns = [
        'bathrooms', 'bedrooms', 'city', 'homeStatus', 'homeType',
        'livingArea', 'price', 'rentZestimate', 'zipcode'
    ]
    df = df[selected_columns]
    
    # Convert DataFrame to CSV format without the index
    csv_data = df.to_csv(index=False)
    
    # Upload the CSV data to the target S3 bucket
    s3_client.put_object(Bucket=target_bucket, Key=f"{target_file_name}.csv", Body=csv_data)
    
    # Return a success response
    return {
        'statusCode': 200,
        'body': json.dumps('CSV conversion and S3 upload completed successfully')
    }
