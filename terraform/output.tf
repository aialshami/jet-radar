#Output repository URLs
output "staging_repo_url"{
  value = aws_ecr_repository.staging_ecr.repository_url
}
output "production_repo_url"{
  value = aws_ecr_repository.production_ecr.repository_url
}