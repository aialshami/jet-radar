terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

# Defining variables
variable "aws_access_key" {
  type = string
}
variable "aws_secret_key" {
  type = string
}

# Configure AWS provider
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = "eu-west-2"
}