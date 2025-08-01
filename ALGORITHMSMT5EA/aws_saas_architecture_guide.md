# AWS Cloud Architecture Guide for MT5 EA SaaS Platform

## Overview
This guide outlines a comprehensive AWS cloud infrastructure for a multi-tenant MT5 Expert Advisor (EA) trading platform with Django/PostgreSQL/React frontend and automated EA deployment.

## Business Requirements Summary
- **Tiers**: Bronze (3 EAs, 1 active), Gold (7 EAs, 3 active), Platinum (20 EAs, 10 active)
- **Multi-tenant**: Isolated EA execution per user
- **Dynamic deployment**: Users can deploy/pause/resume EAs
- **AI recommendations**: Market analysis for EA selection
- **Currency isolation**: Different EAs on different currency pairs
- **Secure broker integration**: User MT5 credentials management

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS CLOUD ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│  [CloudFront CDN] → [ALB] → [ECS Web Services]                 │
│                              ↓                                  │
│  [RDS PostgreSQL] ← [Django API] → [ECS EA Workers]            │
│                              ↓                                  │
│  [ElastiCache Redis] ← [Celery] → [EC2 MT5 Instances]          │
│                              ↓                                  │
│  [S3 Storage] ← [Lambda Functions] → [CloudWatch Monitoring]    │
│                              ↓                                  │
│  [SQS Queues] ← [EventBridge] → [SNS Notifications]            │
└─────────────────────────────────────────────────────────────────┘
```

## Core Infrastructure Components

### 1. Web Application Layer (Frontend/API)

#### 1.1 Amazon ECS (Elastic Container Service)
```yaml
# Django API Service
Service: trading-platform-api
- CPU: 1024 (1 vCPU)
- Memory: 2048 MB
- Desired Count: 2-10 (Auto Scaling)
- Load Balancer: Application Load Balancer
- Health Checks: /health endpoint

# React Frontend Service  
Service: trading-platform-web
- CPU: 512
- Memory: 1024 MB
- Desired Count: 2-5
- CDN: CloudFront distribution
```

#### 1.2 Application Load Balancer (ALB)
- **SSL/TLS**: Certificate Manager for HTTPS
- **Routing**: API requests to Django, static content to React
- **Health Checks**: Automatic unhealthy instance replacement
- **Auto Scaling**: Based on CPU/memory/request count

### 2. Database Layer

#### 2.1 Amazon RDS PostgreSQL
```yaml
Instance: db.r6g.large (or larger for production)
- Multi-AZ: Yes (High Availability)
- Read Replicas: 2 (for analytics/reporting)
- Backup: 30-day automated backups
- Encryption: At rest and in transit
- Connection Pooling: PgBouncer integration
```

#### 2.2 ElastiCache Redis
```yaml
Node Type: cache.r6g.large
- Cluster Mode: Enabled
- Replicas: 2 per shard
- Purpose: Session management, EA status caching, real-time data
- TTL: Configure based on data type
```

### 3. EA Execution Infrastructure

#### 3.1 Dedicated EC2 Instances for MT5
```yaml
Instance Type: c6i.large (Windows Server 2022)
- Purpose: MetaTrader 5 terminal execution
- Auto Scaling Group: 5-50 instances
- Scaling Metrics: CPU, Memory, Active EA count
- AMI: Custom image with MT5, Python 3.13, dependencies
- EBS: gp3 volumes for performance
```

#### 3.2 ECS Tasks for EA Management
```yaml
Service: ea-orchestrator
- CPU: 512
- Memory: 1024 MB
- Purpose: Deploy, monitor, and manage EA instances
- Integration: Docker containers with EA scripts
```

## Multi-Tenant EA Isolation

### 1. Container-Based Isolation
```python
# Docker container per user EA instance
{
    "user_id": "user_123",
    "ea_type": "trend_following",
    "symbol": "EURUSD", 
    "container_id": "ea_container_abc123",
    "ec2_instance": "i-0123456789abcdef",
    "status": "running|paused|stopped",
    "resource_limits": {
        "cpu": 0.25,  # 25% of instance CPU
        "memory": 256  # MB
    }
}
```

### 2. Instance Allocation Strategy
```python
# Smart instance allocation
def allocate_ea_instance(user_tier, ea_type, symbol):
    """
    Bronze: Max 1 EA per user
    Gold: Max 3 EAs per user, different symbols
    Platinum: Max 10 EAs per user, different symbols
    """
    available_instances = get_instances_with_capacity()
    
    # Find instance with lowest load
    target_instance = min(available_instances, 
                         key=lambda x: x.current_ea_count)
    
    # Deploy EA container to target instance
    deploy_ea_container(target_instance, user_id, ea_config)
```

## Database Schema Design

### 1. Core Models
```python
# Django Models Structure

class User(AbstractUser):
    tier = models.CharField(choices=['bronze', 'gold', 'platinum'])
    mt5_login = models.CharField(max_length=50, encrypted=True)
    mt5_password = models.CharField(max_length=100, encrypted=True) 
    mt5_server = models.CharField(max_length=100)
    subscription_active = models.BooleanField(default=False)
    max_concurrent_eas = models.IntegerField()  # 1, 3, or 10

class EATemplate(models.Model):
    name = models.CharField(max_length=100)  # "Trend Following", "Grid Trading"
    script_name = models.CharField(max_length=100)  # "mt5_trend_following_ea.py"
    tier_access = models.JSONField()  # ["bronze", "gold", "platinum"]
    default_config = models.JSONField()
    resource_requirements = models.JSONField()

class UserEAInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ea_template = models.ForeignKey(EATemplate, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)  # "EURUSD", "GBPUSD"
    status = models.CharField(choices=['deploying', 'running', 'paused', 'stopped', 'error'])
    container_id = models.CharField(max_length=100, null=True)
    ec2_instance_id = models.CharField(max_length=50, null=True)
    config = models.JSONField()  # Custom EA configuration
    created_at = models.DateTimeField(auto_now_add=True)
    
class EAPerformance(models.Model):
    ea_instance = models.ForeignKey(UserEAInstance, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    equity = models.DecimalField(max_digits=12, decimal_places=2)
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2)
    trades_count = models.IntegerField()
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
```

## EA Deployment Pipeline

### 1. Celery Task Queue System
```python
# Celery tasks for EA management
from celery import shared_task
import boto3

@shared_task
def deploy_ea_instance(user_id, ea_template_id, symbol, config):
    """Deploy new EA instance for user"""
    
    # 1. Validate user limits
    user = User.objects.get(id=user_id)
    active_count = user.usereainstance_set.filter(status='running').count()
    
    if active_count >= user.max_concurrent_eas:
        return {"error": "Maximum EA limit reached"}
    
    # 2. Find available EC2 instance
    ec2_instance = find_least_loaded_instance()
    
    # 3. Create Docker container
    container_config = {
        "image": "mt5-ea-runner:latest",
        "environment": {
            "EA_SCRIPT": ea_template.script_name,
            "MT5_LOGIN": decrypt(user.mt5_login),
            "MT5_PASSWORD": decrypt(user.mt5_password),
            "MT5_SERVER": user.mt5_server,
            "SYMBOL": symbol,
            "USER_ID": user_id,
            **config
        },
        "resource_limits": {
            "cpu": 0.25,
            "memory": 256 * 1024 * 1024  # 256MB
        }
    }
    
    # 4. Deploy to EC2 instance
    container_id = deploy_container(ec2_instance.id, container_config)
    
    # 5. Update database
    UserEAInstance.objects.create(
        user=user,
        ea_template_id=ea_template_id,
        symbol=symbol,
        status='running',
        container_id=container_id,
        ec2_instance_id=ec2_instance.id,
        config=config
    )
    
    return {"success": True, "container_id": container_id}

@shared_task 
def pause_ea_instance(ea_instance_id):
    """Pause running EA instance"""
    ea_instance = UserEAInstance.objects.get(id=ea_instance_id)
    
    # Stop container but keep it
    stop_container(ea_instance.container_id)
    ea_instance.status = 'paused'
    ea_instance.save()

@shared_task
def resume_ea_instance(ea_instance_id):
    """Resume paused EA instance"""
    ea_instance = UserEAInstance.objects.get(id=ea_instance_id)
    
    # Start container
    start_container(ea_instance.container_id)
    ea_instance.status = 'running' 
    ea_instance.save()
```

### 2. Auto Scaling Configuration
```python
# Auto Scaling Logic
class EAAutoScaler:
    def scale_ec2_instances(self):
        """Auto scale EC2 instances based on demand"""
        
        # Get current metrics
        total_eas = UserEAInstance.objects.filter(status='running').count()
        current_instances = get_active_ec2_instances()
        
        # Calculate required instances (5 EAs per instance)
        required_instances = math.ceil(total_eas / 5)
        current_count = len(current_instances)
        
        if required_instances > current_count:
            # Scale up
            for _ in range(required_instances - current_count):
                launch_new_instance()
                
        elif required_instances < current_count - 1:  # Keep 1 buffer
            # Scale down
            terminate_least_used_instance()
```

## AI Market Analysis Integration

### 1. AI Service Architecture
```python
# AI Recommendation Service
class MarketAnalysisAI:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime')
        
    def get_ea_recommendations(self, user_tier, current_market_data):
        """Get AI recommendations for EA deployment"""
        
        prompt = f"""
        Market Analysis for EA Selection:
        
        Current Market Data:
        - Major pairs volatility: {current_market_data['volatility']}
        - Trend strength: {current_market_data['trend_strength']} 
        - Market sentiment: {current_market_data['sentiment']}
        
        User Tier: {user_tier}
        Available EAs: {self.get_available_eas(user_tier)}
        
        Recommend the best EA strategy and currency pairs for current market conditions.
        """
        
        response = self.bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        return json.loads(response['body'].read())
```

### 2. Real-time Market Data Integration
```python
# WebSocket service for real-time updates
import asyncio
import websockets

class MarketDataService:
    async def stream_market_data(self):
        """Stream real-time market data to AI analysis"""
        
        while True:
            # Get latest market data
            market_data = await self.fetch_market_data()
            
            # Update AI recommendations
            recommendations = self.ai_service.get_ea_recommendations(
                user_tier='all',
                current_market_data=market_data
            )
            
            # Broadcast to connected users
            await self.broadcast_recommendations(recommendations)
            
            await asyncio.sleep(300)  # Update every 5 minutes
```

## Security & Compliance

### 1. MT5 Credentials Encryption
```python
from cryptography.fernet import Fernet
import boto3

class SecureCredentials:
    def __init__(self):
        # Use AWS KMS for encryption keys
        self.kms_client = boto3.client('kms')
        self.key_id = 'arn:aws:kms:region:account:key/key-id'
        
    def encrypt_credentials(self, mt5_login, mt5_password):
        """Encrypt MT5 credentials using AWS KMS"""
        
        # Generate data key
        response = self.kms_client.generate_data_key(
            KeyId=self.key_id,
            KeySpec='AES_256'
        )
        
        # Encrypt credentials
        fernet = Fernet(base64.urlsafe_b64encode(response['Plaintext'][:32]))
        encrypted_login = fernet.encrypt(mt5_login.encode())
        encrypted_password = fernet.encrypt(mt5_password.encode())
        
        return {
            'encrypted_login': encrypted_login,
            'encrypted_password': encrypted_password,
            'data_key': response['CiphertextBlob']
        }
```

### 2. Network Security
```yaml
# VPC Configuration
VPC:
  CIDR: 10.0.0.0/16
  
Subnets:
  Public: 
    - 10.0.1.0/24 (ALB, NAT Gateway)
    - 10.0.2.0/24 (ALB, NAT Gateway)
  Private:
    - 10.0.10.0/24 (Web services)
    - 10.0.11.0/24 (Web services)
    - 10.0.20.0/24 (EA instances)
    - 10.0.21.0/24 (EA instances)
  Database:
    - 10.0.30.0/24 (RDS, ElastiCache)
    - 10.0.31.0/24 (RDS, ElastiCache)

Security Groups:
  ALB: Ports 80, 443 from 0.0.0.0/0
  Web: Port 8000 from ALB only
  EA: Port 22 from Web services only
  Database: Port 5432 from Web/EA only
```

## Monitoring & Observability

### 1. CloudWatch Dashboards
```python
# Custom CloudWatch metrics
class EAMonitoring:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        
    def publish_ea_metrics(self, ea_instance_id, metrics):
        """Publish EA performance metrics"""
        
        self.cloudwatch.put_metric_data(
            Namespace='TradingPlatform/EA',
            MetricData=[
                {
                    'MetricName': 'ProfitLoss',
                    'Dimensions': [
                        {'Name': 'EAInstanceId', 'Value': ea_instance_id}
                    ],
                    'Value': metrics['profit_loss'],
                    'Unit': 'None'
                },
                {
                    'MetricName': 'TradeCount',
                    'Dimensions': [
                        {'Name': 'EAInstanceId', 'Value': ea_instance_id}
                    ],
                    'Value': metrics['trade_count'],
                    'Unit': 'Count'
                }
            ]
        )
```

### 2. Automated Alerts
```yaml
# CloudWatch Alarms
Alarms:
  EA_High_Loss:
    MetricName: ProfitLoss
    Threshold: -1000  # $1000 loss
    ComparisonOperator: LessThanThreshold
    Action: SNS notification + auto-pause EA
    
  Instance_High_CPU:
    MetricName: CPUUtilization
    Threshold: 80
    Action: Scale up EC2 instances
    
  Database_Connections:
    MetricName: DatabaseConnections
    Threshold: 80
    Action: Alert and scale read replicas
```

## Cost Optimization

### 1. Instance Types & Sizing
```yaml
Development Environment:
  Web: t3.medium x 2 = $60/month
  EA: t3.large x 2 = $120/month
  RDS: db.t3.medium = $70/month
  Total: ~$250/month

Production Environment:
  Web: c6i.large x 4 = $280/month
  EA: c6i.large x 10-50 = $700-3500/month
  RDS: db.r6g.xlarge = $350/month
  ElastiCache: cache.r6g.large = $200/month
  Total: ~$1500-4500/month (scales with users)
```

### 2. Reserved Instances & Spot
```python
# Cost optimization strategy
Cost_Optimization:
  Reserved_Instances: 
    - Web services (predictable load)
    - Database instances
    - 1-year term for 30% savings
    
  Spot_Instances:
    - EA workers (fault tolerant)
    - Development environments
    - Up to 70% cost savings
    
  Auto_Scaling:
    - Scale down during low usage
    - Weekend schedules for non-forex EAs
```

## Deployment Strategy

### 1. Infrastructure as Code (Terraform)
```hcl
# terraform/main.tf
module "vpc" {
  source = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
}

module "ecs_cluster" {
  source = "./modules/ecs"
  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.private_subnets
}

module "rds" {
  source = "./modules/rds"
  vpc_id = module.vpc.vpc_id
  db_subnets = module.vpc.database_subnets
}

module "ea_infrastructure" {
  source = "./modules/ea-workers"
  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.private_subnets
}
```

### 2. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy Trading Platform

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t trading-platform-web ./frontend
          docker build -t trading-platform-api ./backend
          docker build -t mt5-ea-runner ./ea-runner
          
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker push $ECR_REGISTRY/trading-platform-web:latest
          docker push $ECR_REGISTRY/trading-platform-api:latest
          docker push $ECR_REGISTRY/mt5-ea-runner:latest
          
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster production --service web --force-new-deployment
          aws ecs update-service --cluster production --service api --force-new-deployment
```

## Getting Started Checklist

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Set up AWS VPC and networking
- [ ] Deploy RDS PostgreSQL with Multi-AZ
- [ ] Set up ECS cluster for web services
- [ ] Configure Application Load Balancer
- [ ] Deploy Django API and React frontend
- [ ] Set up ElastiCache Redis cluster

### Phase 2: EA Infrastructure (Week 3-4)
- [ ] Create custom AMI with MT5 + Python
- [ ] Set up Auto Scaling Group for EA instances
- [ ] Implement container orchestration
- [ ] Build EA deployment pipeline
- [ ] Set up Celery task queue system
- [ ] Implement user EA limits and isolation

### Phase 3: AI & Monitoring (Week 5-6)
- [ ] Integrate AWS Bedrock for AI recommendations
- [ ] Set up real-time market data feeds
- [ ] Implement CloudWatch monitoring
- [ ] Create performance dashboards
- [ ] Set up automated alerts and notifications
- [ ] Implement cost monitoring and optimization

### Phase 4: Security & Compliance (Week 7-8)
- [ ] Implement MT5 credential encryption (AWS KMS)
- [ ] Set up WAF and security groups
- [ ] Implement audit logging
- [ ] Set up backup and disaster recovery
- [ ] Performance testing and optimization
- [ ] Security penetration testing

## Estimated Costs

### Development Environment
- Infrastructure: $250/month
- Development team: $15,000/month (3 developers)
- AWS credits: -$1,000 (startup credits)

### Production (Initial Launch)
- Infrastructure: $1,500/month (100 users)
- Scaling: Linear growth $30/month per 100 users
- At 1,000 users: ~$4,500/month infrastructure

### Revenue Projections
- Bronze ($29/month): Break-even at ~50 users
- Gold ($79/month): Break-even at ~20 users  
- Platinum ($199/month): Break-even at ~8 users

This architecture provides a robust, scalable foundation for your MT5 EA SaaS platform with proper multi-tenancy, security, and cost optimization!
