###############################################################################
# main.tf – Infra: AWS SQS + SNS + Lambda
#   • SNS Topic “OrderPlaced”
#   • SQS colas (standard + FIFO) y sus DLQ
#   • Subscriptions SNS → SQS (fan-out)
#   • Lambdas Orders, Billing y Status with event source mapping
#   • IAM minimal roles
#   • CloudWatch alarms
###############################################################################

###############################################################################
# Vars
###############################################################################
variable "environment" { 
    type = string  
    default = "dev" 
}

###############################################################################
# KMS – cipher for SQS/SNS
###############################################################################
resource "aws_kms_key" "sqs" {
  description             = "KMS key for SQS & SNS – ${var.environment}"
  deletion_window_in_days = 7
}

############################################################################### 
# S3 buckets
############################################################################### 
resource "aws_s3_bucket" "billings_bucket" {
  bucket = "billings-${var.environment}"
}

resource "aws_s3_bucket" "orders_bucket" {
  bucket = "orders-${var.environment}"
}

###############################################################################
# SNS Topic
###############################################################################
resource "aws_sns_topic" "order_placed" {
  name              = "OrderPlaced-${var.environment}"
#   fifo_topic                  = true
#   content_based_deduplication = true    

  kms_master_key_id = aws_kms_key.sqs.arn
  tags = {
    Project = "order-service"
    Env     = var.environment
  }
}

###############################################################################
# SQS – DLQs
###############################################################################
resource "aws_sqs_queue" "orders_dlq" {
  name                       = "orders-dlq-${var.environment}"
  message_retention_seconds  = 1209600 # 14 d
  kms_master_key_id          = aws_kms_key.sqs.arn
}

resource "aws_sqs_queue" "billing_dlq" {
  name                       = "billing-dlq-${var.environment}"
#   fifo_queue                 = true
  message_retention_seconds  = 1209600
  kms_master_key_id          = aws_kms_key.sqs.arn
}

###############################################################################
# SQS – main queues
###############################################################################
resource "aws_sqs_queue" "orders" {
  name                       = "orders-${var.environment}"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600 # 4 d
  kms_master_key_id          = aws_kms_key.sqs.arn

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orders_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "billing" {
  name                       = "billing-${var.environment}"
#   fifo_queue                 = true
#   content_based_deduplication = true
  visibility_timeout_seconds = 60
  kms_master_key_id          = aws_kms_key.sqs.arn

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.billing_dlq.arn
    maxReceiveCount     = 5
  })
}

###############################################################################
# SQS queue policies – allows SNS to send messages
###############################################################################
data "aws_iam_policy_document" "orders_sns_send" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.orders.arn]
    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.order_placed.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "orders_policy" {
  queue_url = aws_sqs_queue.orders.id
  policy    = data.aws_iam_policy_document.orders_sns_send.json
}

data "aws_iam_policy_document" "billing_sns_send" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.billing.arn]
    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.order_placed.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "billing_policy" {
  queue_url = aws_sqs_queue.billing.id
  policy    = data.aws_iam_policy_document.billing_sns_send.json
}

###############################################################################
# Subscriptions SNS → SQS
###############################################################################
resource "aws_sns_topic_subscription" "orders_sub" {
  topic_arn             = aws_sns_topic.order_placed.arn
  protocol              = "sqs"
  endpoint              = aws_sqs_queue.orders.arn
  raw_message_delivery  = true
}

resource "aws_sns_topic_subscription" "billing_sub" {
  topic_arn             = aws_sns_topic.order_placed.arn
  protocol              = "sqs"
  endpoint              = aws_sqs_queue.billing.arn
  raw_message_delivery  = true
}

###############################################################################
# IAM Roles and policies for Lambda
###############################################################################
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Generic role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name               = "lambda-exec-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

# Inline policy – SQS access + logs
resource "aws_iam_role_policy" "lambda_exec_policy" {
  name   = "lambda-exec-policy"
  role   = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = [
          aws_sqs_queue.orders.arn,
          aws_sqs_queue.billing.arn
        ]
      }
    ]
  })
}

# Lambda resources

resource "archive_file" "lambda_orders_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/orders"
  output_path = "${path.module}/../../src/orders/lambda_orders.zip"
}

resource "archive_file" "lambda_billings_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/billings"
  output_path = "${path.module}/../../src/billings/lambda_billings.zip"
}

resource "archive_file" "lambda_status_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/status"
  output_path = "${path.module}/../../src/status/lambda_status.zip"
}


###############################################################################
# Lambda functions
###############################################################################
resource "aws_lambda_function" "orders_fn" {
  function_name    = "LambdaOrders-${var.environment}"
  filename         = archive_file.lambda_orders_zip.output_path
  source_code_hash = archive_file.lambda_orders_zip.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  # architectures    = ["arm64"]
  memory_size      = 512
  timeout          = 120
  role             = aws_iam_role.lambda_exec.arn
  environment {
    variables = {
      STAGE = var.environment
    }
  }
}

resource "aws_lambda_function" "billing_fn" {
  function_name    = "LambdaBilling-${var.environment}"
  filename         = archive_file.lambda_billings_zip.output_path
  source_code_hash = archive_file.lambda_billings_zip.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  # architectures    = ["arm64"]
  memory_size      = 512
  timeout          = 120
  role             = aws_iam_role.lambda_exec.arn
}

resource "aws_lambda_function" "status_fn" {
  function_name    = "LambdaStatus-${var.environment}"
  filename         = archive_file.lambda_status_zip.output_path
  source_code_hash = archive_file.lambda_status_zip.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  # architectures    = ["arm64"]
  memory_size      = 512
  timeout          = 120
  role             = aws_iam_role.lambda_exec.arn
}

###############################################################################
# Event source mappings – bind queues to Lambdas
###############################################################################
resource "aws_lambda_event_source_mapping" "orders_es" {
  event_source_arn = aws_sqs_queue.orders.arn
  function_name    = aws_lambda_function.orders_fn.arn
  batch_size       = 10
  maximum_batching_window_in_seconds = 0
  enabled          = true
}

resource "aws_lambda_event_source_mapping" "billing_es" {
  event_source_arn                       = aws_sqs_queue.billing.arn
  function_name                          = aws_lambda_function.billing_fn.arn
  batch_size                             = 1          # FIFO => 1
  maximum_batching_window_in_seconds     = 0
  enabled                                = true
}

###############################################################################
# CloudWatch alarms – DLQ and latency
###############################################################################
resource "aws_cloudwatch_metric_alarm" "orders_dlq_alarm" {
  alarm_name          = "OrdersDLQNotEmpty-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  dimensions = {
    QueueName = aws_sqs_queue.orders_dlq.name
  }
  alarm_description = "Messages in Orders DLQ"
}

resource "aws_cloudwatch_metric_alarm" "orders_latency_alarm" {
  alarm_name          = "OrdersOldestMessage-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 300
  dimensions = {
    QueueName = aws_sqs_queue.orders.name
  }
  alarm_description = "Order queue is backing up (>5 min old)"
}

###############################################################################
# Global tags
###############################################################################
locals {
  common_tags = {
    Project = "order-service"
    Env     = var.environment
    Owner   = "backend-team"
  }
}
