# End-to-End Python ETL Pipeline

## Overview

This project demonstrates the construction of an end-to-end Python ETL (Extract, Transform, Load) pipeline using AWS services. The pipeline is designed to extract real estate property data from the Zillow Rapid API and process it through various AWS components.

### Extraction

- **API**: Data is extracted from the Zillow Rapid API.
- **Python**: A Python script is used to connect and pull data from the API.

### AWS Services Used

1. **Amazon EC2**: Hosts the Apache Airflow instance that orchestrates the ETL pipeline.
2. **Amazon S3**: Serves as the landing and intermediate zones for raw and processed data.
3. **AWS Lambda**: Automates the data flow between S3 buckets and data transformation.
4. **Amazon Redshift**: Hosts the transformed data for querying and analysis.
5. **AWS QuickSight**: Provides BI tools for data visualization.

### Data Processing Steps

1. Data is initially loaded into an S3 bucket (landing zone).
2. A Lambda function triggers to move data to another S3 bucket, ensuring data immutability in the landing zone.
3. Another Lambda function performs data transformation.
4. Transformed data is loaded into a different S3 bucket.
5. An S3 Key Sensor checks for the presence of transformed data before loading it into Redshift.
6. Data is finally loaded into an Amazon Redshift cluster.

### Orchestration

- **Apache Airflow**: Orchestrates the pipeline, running on an Amazon EC2 instance.
- **Python Operator**: Connects to the Zillow Rapid API to extract data.
- **Bash Operator**: Moves data from EC2 to the S3 landing zone.

## Visualization

After loading into Redshift, AWS QuickSight visualizes the data, providing insights into the real estate properties information.
