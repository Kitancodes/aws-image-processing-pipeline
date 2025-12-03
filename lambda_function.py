import json
import boto3
import base64
from datetime import datetime

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')


SNS_TOPIC_ARN = 'arn:aws:sns:eu-north-1:839950285905:image-processing-notifications' 

def lambda_handler(event, context):
    """
    Image processing pipeline using boto3 only:
    - Copy image with metadata
    - Add processing timestamp
    - Tag as processed
    """
    
    # Get bucket and object key from S3 event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Define output bucket
    output_bucket = 'myimage-processor-output'
    
    try:
        # Get image from S3
        response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
        image_data = response['Body'].read()
        content_type = response.get('ContentType', 'image/jpeg')
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate output filename
        import os
        base_name = os.path.splitext(object_key)[0]
        extension = os.path.splitext(object_key)[1]
        output_key = f"processed_{base_name}{extension}"
        
        # Upload to output bucket with metadata
        s3_client.put_object(
            Bucket=output_bucket,
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
        
        # Log success
        print(f"Successfully processed: {object_key} -> {output_key}")
        print(f"Timestamp: {timestamp}")
        
        # Send SNS notification
        try:
            message = f"""
Image Processing Complete!

Original File: {object_key}
Processed File: {output_key}
Source Bucket: {source_bucket}
Output Bucket: {output_bucket}
Timestamp: {timestamp}
Status: SUCCESS

Your image has been successfully processed and is available in the output bucket.
            """
            
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='✅ Image Processing Completed',
                Message=message
            )
            print("SNS notification sent successfully")
        except Exception as sns_error:
            print(f"SNS notification failed: {str(sns_error)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Image processed successfully',
                'input': f'{source_bucket}/{object_key}',
                'output': f'{output_bucket}/{output_key}',
                'timestamp': timestamp,
                'note': 'Image copied with processing metadata and tags'
            })
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        
        # Send error notification
        try:
            error_message = f"""
Image Processing FAILED!

Original File: {object_key}
Source Bucket: {source_bucket}
Error: {str(e)}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Please check CloudWatch logs for more details.
            """
            
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='❌ Image Processing Failed',
                Message=error_message
            )
        except:
            pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing image',
                'error': str(e)
            })
        }
