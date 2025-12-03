import json
import boto3
from datetime import datetime
import os

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:839950285905:image-processing-notifications'

INPUT_BUCKET = 'myimage-processor-input'
OUTPUT_BUCKET = 'myimage-processor-output'

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    try:
        response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
        image_data = response['Body'].read()
        content_type = response.get('ContentType', 'image/jpeg')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_name, extension = os.path.splitext(object_key)
        output_key = f"processed_{base_name}{extension}"
        
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=output_key,
            Body=image_data,
            ContentType=content_type,
            Metadata={
                'original-file': object_key,
                'processed-date': timestamp,
                'processing-status': 'completed',
                'pipeline': 'aws-lambda-image-processor'
            },
            Tagging=f'ProcessedBy=Lambda&Timestamp={timestamp.replace(" ", "T")}'
        )
        
        print(f"Processed {object_key} -> {output_key}")
        
        try:
            message = f"""
Image Processing Complete!

Original File: {object_key}
Processed File: {output_key}
Source Bucket: {source_bucket}
Output Bucket: {OUTPUT_BUCKET}
Timestamp: {timestamp}
Status: SUCCESS
"""
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='Image Processing Completed',
                Message=message
            )
        except Exception as sns_error:
            print(f"SNS notification failed: {sns_error}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image processed successfully',
                'input': f'{source_bucket}/{object_key}',
                'output': f'{OUTPUT_BUCKET}/{output_key}',
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error processing image: {e}")
        try:
            error_message = f"""
Image Processing FAILED!

Original File: {object_key}
Source Bucket: {source_bucket}
Error: {e}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='Image Processing Failed',
                Message=error_message
            )
        except Exception as sns_error:
            print(f"Failed to send error SNS: {sns_error}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing image',
                'error': str(e)
            })
        }
