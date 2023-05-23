# Create an S3 resource bucket
resource "aws_s3_bucket" "jet_bucket" {
  bucket = "jet-bucket"
}