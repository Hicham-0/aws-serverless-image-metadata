variable "aws_region" {

  description = "the aws region to deploy the resources"
  type        = string
  default     = "us-east-1"

}

variable "project" {
  description = "the project name "
  type        = string
  default     = "serverless-app"

}