#Create ECR repositories
resource "aws_ecr_repository" "staging_ecr" {
  name                 = "jet-staging-repo"
}

resource "aws_ecr_repository" "production_ecr" {
  name                 = "jet-production-repo"
}

