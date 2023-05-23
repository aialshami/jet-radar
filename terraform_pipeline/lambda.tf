# Find lambda IAM policy
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}


# Find lambda IAM policy document
data aws_iam_policy_document lambda_s3 {
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListObjects"
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.jet_bucket.bucket}/*"
    ]
  }
}


# Create lambda IAM policy
resource aws_iam_policy lambda_s3 {
  name        = "lambda-s3-permissions"
  description = "Contains S3 put permission for lambda"
  policy      = data.aws_iam_policy_document.lambda_s3.json
}


# Creata lambda IAM role
resource "aws_iam_role" "jet_iam_lambda" {
  name               = "jet_iam_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}


# Attach lambda IAM policy and IAM role together
resource aws_iam_role_policy_attachment lambda_policy_attach {
    role       = aws_iam_role.jet_iam_lambda.name
    policy_arn = aws_iam_policy.lambda_s3.arn
}


# Create staging lambda function that will run every 10 mins
resource "aws_lambda_function" "jet_staging_lambda" {
  function_name = "jet_staging_lambda"
  role          = aws_iam_role.jet_iam_lambda.arn
  memory_size   = 1024
  timeout       = 120
  image_uri     = "${var.account_id}.dkr.ecr.eu-west-2.amazonaws.com/jet-staging-repo:latest"
  package_type  = "Image"
  architectures = ["x86_64"]

  # Define environment variables in lambda
  environment {
    variables = {
        RAPIDAPI_KEY=var.rapidapi_key
        RAPIDAPI_HOST=var.rapidapi_host

        DB_HOST=aws_db_instance.jet_db.endpoint
        DB_NAME=aws_db_instance.jet_db.name
        DB_USER=var.username
        DB_PASSWORD=var.password
        DB_PORT=aws_db_instance.jet_db.port

        STAGING_TABLE_NAME=var.staging_table
        STAGING_SCHEMA=var.staging_schema

        ACCESS_KEY=var.aws_access_key
        SECRET_KEY=var.aws_secret_key

        S3_BUCKET_NAME=aws_s3_bucket.jet_bucket.bucket
        CELEB_INFO=var.celeb_info
    }
  }
}


# Create cloudwatch event for staging lambda
resource "aws_cloudwatch_event_rule" "jet_ten_mins" {
  name                = "jet_ten_mins"
  schedule_expression = "rate(10 minutes)"

}


# Create staging schedule target for staging lambda function 
resource "aws_cloudwatch_event_target" "jet_target_ten_mins" {
  rule = aws_cloudwatch_event_rule.jet_ten_mins.name
  arn  = aws_lambda_function.jet_staging_lambda.arn
}


# Create staging trigger prevention for staging lambda
resource "aws_lambda_permission" "allow_call_jet_ten_mins" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.jet_staging_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.jet_ten_mins.arn
}


# Create production lambda function that will run every 24 hours
resource "aws_lambda_function" "jet_production_lambda" {
  function_name = "jet_production_lambda"
  role          = aws_iam_role.jet_iam_lambda.arn
  memory_size   = 1024
  timeout       = 120
  image_uri     = "${var.account_id}.dkr.ecr.eu-west-2.amazonaws.com/jet-production-repo:latest"
  package_type  = "Image"
  architectures = ["x86_64"]

  # Define environment variables in lambda
  environment {
    variables = {
        RAPIDAPI_KEY=var.rapidapi_key
        RAPIDAPI_HOST=var.rapidapi_host

        DB_HOST=aws_db_instance.jet_db.endpoint
        DB_NAME=aws_db_instance.jet_db.name
        DB_USER=var.username
        DB_PASSWORD=var.password
        DB_PORT=aws_db_instance.jet_db.port

        STAGING_TABLE_NAME=var.staging_table
        STAGING_SCHEMA=var.staging_schema
        PRODUCTION_SCHEMA=var.production_schema

        ACCESS_KEY=var.aws_access_key
        SECRET_KEY=var.aws_secret_key

        S3_BUCKET_NAME=aws_s3_bucket.jet_bucket.bucket
        CELEB_INFO=var.celeb_info
    }
  }
}


# Create cloudwatch event for production lambda
resource "aws_cloudwatch_event_rule" "jet_daily" {
  name                = "jet_daily"
  schedule_expression = "rate(24 hours)"

}


# Create staging schedule target for production lambda function 
resource "aws_cloudwatch_event_target" "jet_target_daily" {
  rule = aws_cloudwatch_event_rule.jet_daily.name
  arn  = aws_lambda_function.jet_production_lambda.arn
}


# Create staging trigger prevention
resource "aws_lambda_permission" "allow_call_daily" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.jet_production_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.jet_daily.arn
}
