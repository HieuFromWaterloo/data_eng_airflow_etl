import json
import boto3

# Init s3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extracting the source bucket and object key from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
   
    # Define the target bucket where the object will be copied
    target_bucket = 'ENTER_S3_LOAD_BUCKET_HERE'
    
    # Define the copy source dictionary
    copy_source = {'Bucket': source_bucket, 'Key': object_key}
   
    # Wait for the source object to exist before attempting the copy
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    
    # Copy the object to the target bucket
    s3_client.copy_object(Bucket=target_bucket, Key=object_key, CopySource=copy_source)
    
    # Return a success response
    return {
        'statusCode': 200,
        'body': json.dumps('lambda func: json loaded successfully')
    }
