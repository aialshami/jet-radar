#Creates SNS topic
resource "aws_sns_topic" "jet-report-topic" {
    name = "jet-report-topic"
}


#Creates SNS topic policy
resource "aws_sns_topic_policy" "default" {
    arn = aws_sns_topic.jet-report-topic.arn
    policy = data.aws_iam_policy_document.sns_topic_policy.json
}


#Changes SNS topic policy permissions
data "aws_iam_policy_document" "sns_topic_policy"{
    policy_id = "__default_policy_ID"
    #Account holders will have access to full permissions
    statement {
      actions = [
        "SNS:Publish",
        "SNS:RemovePermission",
        "SNS:SetTopicAttributes",
        "SNS:DeleteTopic",
        "SNS:ListSubscriptionsByTopic",
        "SNS:GetTopicAttributes",
        "SNS:AddPermission",
        "SNS:Subscribe"
      ]
      condition {
        test    ="StringEquals"
        variable = "AWS:SourceOwner"
        values = [
            var.account_id
        ]
      }
      effect = "Allow"
      principals {
        type = "AWS"
        identifiers = ["*"]
      }
      
      resources = [
      "arn:aws:sns:${var.region}:${var.account_id}:${aws_sns_topic.jet-report-topic.name}"
    ]
      sid = "__default_statement_ID"
    }

    #Non account holders can only subscribe
    statement {
      actions = [
        "SNS:Subscribe"
      ]
      effect = "Allow"
      principals {
        type = "AWS"
        identifiers = ["*"]
      }
      resources = [
      "arn:aws:sns:${var.region}:${var.account_id}:${aws_sns_topic.jet-report-topic.name}"
    ]
      sid = "__console_sub_0"
    }
}