output "aws_bucket_id" {
  description = "The ID of the S3 bucket created for Terraform state storage"
  value       = aws_s3_bucket.terraform_state.id
}