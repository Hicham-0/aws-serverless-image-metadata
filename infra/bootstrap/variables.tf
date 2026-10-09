variable "aws_region" {

  description = "the aws region to deploy the s3 for remote bakcend "
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "the project name "
  type        = string
  default     = "serverless-pipeline-project"

}