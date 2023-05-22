# Defining provider to use and its versions
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
variable "username" {
  type = string
}
variable "password" {
  type = string
}
variable "region" {
  type = string
}
variable "account_id" {
  type = string
}

# Configure AWS provider
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.region
}

# Use existing VPC
data "aws_vpc" "c7-vpc" {
  id = "vpc-010fd888c94cf5102"
}

# Use existing subnet
data "aws_db_subnet_group" "c7-subnets" {
  name = "c7-db-subnet-group"
}


# Use existing security group
data "aws_security_group" "c7-remote-access" {
  name   = "c7-remote-access"
  vpc_id = data.aws_vpc.c7-vpc.id
  id     = "sg-01745c9fa38b8ed68"
}
