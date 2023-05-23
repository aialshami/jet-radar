#Create ECR repositories
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

resource "aws_ecr_repository" "staging_ecr" {
  name                 = "jet-staging-repo"
}

resource "aws_ecr_repository" "production_ecr" {
  name                 = "jet-production-repo"
}

