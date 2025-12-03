# AWS Serverless Image Processing Pipeline

## Overview
An automated, serverless image processing pipeline built on AWS using Lambda, S3, and SNS. This project demonstrates event-driven architecture, cloud automation, and DevOps best practices.

## Architecture

```
User Upload → S3 Input Bucket → Lambda Function → S3 Output Bucket
                                      ↓
                              SNS Notifications + CloudWatch Monitoring
```

### Components
- **S3 Input Bucket**: `myimage-processor-input` - Receives raw images
- **AWS Lambda**: `image-processor-function` - Processes images automatically
- **S3 Output Bucket**: `myimage-processor-output` - Stores processed images
- **SNS**: Email notifications for processing status
- **CloudWatch**: Logging and monitoring

## Features

- **Serverless Architecture** - No infrastructure management required  
- **Event-Driven Processing** - Automatic trigger on image upload  
- **Metadata Tagging** - Adds processing timestamps and tags  
- **Error Handling** - Comprehensive error logging and notifications  
- **Scalable** - Handles multiple concurrent image uploads   

## Technical Stack

- **Cloud Platform**: AWS
- **Compute**: AWS Lambda (Python 3.14)
- **Storage**: Amazon S3
- **Notifications**: Amazon SNS
- **Monitoring**: Amazon CloudWatch

## How It Works

1. User uploads an image to the input S3 bucket
2. S3 triggers a Lambda function automatically
3. Lambda processes the image:
   - Adds metadata (timestamp, processing status)
   - Tags the image for tracking
   - Copies to output bucket
4. SNS sends email notification on success/failure
5. CloudWatch logs all processing events

## Project Structure

```
aws-image-processor/
├── lambda_function.py          # Main Lambda function code
├── README.md                   # Project documentation
├── architecture-diagram.png    # Visual architecture
└── screenshots/                # Demo screenshots
    ├── input-bucket.png
    ├── output-bucket.png
    └── cloudwatch-logs.png
```

## Setup Instructions

### Prerequisites
- AWS Account
- AWS CLI configured
- Basic understanding of AWS services

### Deployment Steps

1. **Create S3 Buckets**
   ```bash
   aws s3 mb s3://myimage-processor-input --region eu-north-1
   aws s3 mb s3://myimage-processor-output --region eu-north-1
   ```

2. **Create Lambda Function**
   - Runtime: Python 3.14
   - Timeout: 1 minute
   - Memory: 512 MB
   - Attach IAM role with S3 and SNS permissions

3. **Configure S3 Trigger**
   - Event: All object create events
   - Bucket: myimage-processor-input

4. **Create SNS Topic**
   ```bash
   aws sns create-topic --name image-processing-notifications --region eu-north-1
   ```

5. **Deploy Lambda Code**
   - Copy `lambda_function.py` to Lambda
   - Update SNS_TOPIC_ARN with your topic ARN
   - Deploy

### Testing

1. Upload an image to the input bucket:
   ```bash
   aws s3 cp test-image.jpg s3://myimage-processor-input/
   ```

2. Check output bucket after 10-20 seconds:
   ```bash
   aws s3 ls s3://myimage-processor-output/
   ```

3. Verify email notification received

## Use Cases

- **Automated Image Backup**: Process and tag uploaded images
- **Content Management**: Organize images with metadata
- **Audit Trail**: Track when and how images are processed

## Security

- IAM roles with least privilege access
- S3 bucket policies for access control
- Encrypted data at rest (S3 default encryption)
- CloudWatch logs for audit trail

## Lessons Learned

- Event-driven architecture reduces complexity
- Serverless computing eliminates infrastructure overhead
- Proper error handling is critical for production systems
- Monitoring and logging are essential for debugging

## Author

**Olakitan Oladimeji**  
DevOps Engineer | Cloud Enthusiast  

---
