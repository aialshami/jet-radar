#Create ECR repositories
resource "aws_ecr_repository" "staging_ecr" {
  name                 = "jet-staging-repo"
  image_tag_mutability = "IMMUTABLE"
}

resource "aws_ecr_repository" "production_ecr" {
  name                 = "jet-production-repo"
  image_tag_mutability = "IMMUTABLE"
}

