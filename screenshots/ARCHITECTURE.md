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

## Scalability

- **Concurrent Executions**: Lambda scales automatically (default: 1000 concurrent)
- **Throughput**: S3 can handle thousands of requests per second
- **Bottlenecks**: None identified for typical workloads
- **Cost Scaling**: Pay-per-use model ensures cost efficiency

## Security Considerations

### IAM Roles & Policies
- Lambda execution role with least-privilege permissions
- S3 bucket policies restricting access
- SNS topic access controlled via IAM

### Data Protection
- S3 server-side encryption enabled
- Data in transit encrypted (HTTPS)
- No sensitive data in logs

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

## Cost Analysis

### Lambda Costs
- **Free Tier**: 1M requests/month, 400,000 GB-seconds compute
- **Beyond Free Tier**: $0.20 per 1M requests + $0.0000166667 per GB-second
- **Estimated Cost**: ~$1-5/month for moderate use

### S3 Costs
- **Storage**: $0.023 per GB/month (Standard)
- **Requests**: $0.005 per 1,000 PUT requests
- **Data Transfer**: Free within same region

### SNS Costs
- **Email Notifications**: $0 for first 1,000, then $2 per 100,000
- **Typical Cost**: Near zero for personal projects

### Total Monthly Cost (Estimated)
- Small project (<1000 images/month): **$0-2**
- Medium project (1000-10000 images/month): **$2-10**

## Performance Benchmarks

- **Average Processing Time**: 200-400ms per image
- **Cold Start**: ~500-800ms
- **Warm Execution**: ~200-300ms
- **Throughput**: 100+ images/minute (limited by Lambda concurrency)

## Future Enhancements

### Phase 2: Advanced Processing
- Image resizing (thumbnails, multiple sizes)
- Format conversion (JPEG, PNG, WebP)
- Watermarking
- Compression optimization

### Phase 3: AI/ML Integration
- AWS Rekognition for image analysis
- Object detection and labeling
- Content moderation
- Face detection/blurring

### Phase 4: Infrastructure as Code
- Terraform/CloudFormation templates
- Automated deployment pipeline
- Environment management (dev/staging/prod)

### Phase 5: API Integration
- API Gateway for RESTful access
- Direct upload via API
- Webhook notifications
- Status checking endpoints

## Disaster Recovery

### Backup Strategy
- S3 versioning enabled
- Cross-region replication (optional)
- Regular snapshots

### Recovery Plan
- Lambda functions are stateless (easy to redeploy)
- S3 data is durable (99.999999999% durability)
- CloudWatch logs retained for troubleshooting

## Compliance & Best Practices

- Follows AWS Well-Architected Framework
- Implements least-privilege access
- Enables logging and monitoring
- Uses managed services for reliability
- Cost-optimized architecture
