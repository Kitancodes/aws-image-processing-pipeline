# Architecture Documentation

## System Overview

This serverless image processing pipeline leverages AWS managed services to provide automated, scalable, and cost-effective image processing.

## Architecture Diagram
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ Upload Image
       ▼
┌─────────────────────────┐
│  S3 Input Bucket        │
│  myimage-processor-     │
│  input                  │
└──────┬──────────────────┘
       │ S3 Event Notification
       ▼
┌─────────────────────────┐
│  AWS Lambda             │
│  image-processor-       │
│  function               │
│  - Python 3.14          │
│  - 512MB Memory         │
│  - 60s Timeout          │
└──┬────────┬─────────┬───┘
   │        │         │
   │        │         └──────────┐
   │        │                    │
   │        ▼                    ▼
   │  ┌──────────────┐    ┌─────────────┐
   │  │ CloudWatch   │    │   SNS       │
   │  │ Logs         │    │   Topic     │
   │  └──────────────┘    └──────┬──────┘
   │                             │
   ▼                             ▼
┌─────────────────────────┐  ┌──────────┐
│  S3 Output Bucket       │  │  Email   │
│  myimage-processor-     │  │  Alert   │
│  output                 │  └──────────┘
└─────────────────────────┘
```

## Component Details

### 1. S3 Input Bucket
- **Name**: `myimage-processor-input`
- **Region**: eu-north-1 (Stockholm)
- **Purpose**: Receives raw images from users
- **Event Configuration**: Triggers Lambda on object creation
- **Security**: Bucket policies, encryption at rest

### 2. AWS Lambda Function
- **Name**: `image-processor-function`
- **Runtime**: Python 3.14
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Trigger**: S3 object creation events
- **IAM Role**: Permissions for S3 read/write, SNS publish, CloudWatch logs

**Processing Logic**:
1. Receive S3 event notification
2. Download image from input bucket
3. Add metadata tags (timestamp, processing status)
4. Upload to output bucket with new filename
5. Send SNS notification
6. Log results to CloudWatch

### 3. S3 Output Bucket
- **Name**: `myimage-processor-output`
- **Region**: eu-north-1 (Stockholm)
- **Purpose**: Stores processed images
- **Naming Convention**: `processed_[original-filename]`
- **Metadata**: Processing timestamp, original filename, status

### 4. Amazon SNS
- **Topic Name**: `image-processing-notifications`
- **Purpose**: Email notifications for success/failure
- **Subscribers**: Project owner email
- **Message Types**: Success alerts, error notifications

### 5. CloudWatch Logs
- **Log Group**: `/aws/lambda/image-processor-function`
- **Retention**: 30 days (configurable)
- **Purpose**: Debugging, monitoring, audit trail

## Data Flow

1. **Upload Phase**
   - User uploads image → S3 input bucket
   - S3 generates event notification
   - Event contains: bucket name, object key, timestamp

2. **Processing Phase**
   - Lambda receives event trigger
   - Downloads object from S3
   - Applies processing logic
   - Generates metadata

3. **Storage Phase**
   - Uploads processed image to output bucket
   - Applies tags and metadata
   - Sets appropriate permissions

4. **Notification Phase**
   - Publishes message to SNS topic
   - Email sent to subscribers
   - Logs written to CloudWatch

5. **Monitoring Phase**
   - CloudWatch captures all logs
   - Metrics tracked (invocations, duration, errors)
   - Available for debugging and analysis

### Access Control
- Private S3 buckets (no public access)
- Lambda function not publicly accessible
- SNS subscriptions require confirmation

## Monitoring & Observability

### CloudWatch Metrics
- Lambda invocations
- Duration per execution
- Error count and rate
- Throttles

### Custom Logs
- Processing start/end timestamps
- File names and sizes
- Success/failure status
- Error details

### Alerting
- Email notifications via SNS
- CloudWatch alarms (can be configured)
- Error tracking
