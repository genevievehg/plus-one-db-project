terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket = "nc-plus-one-backend"
    key = "s3-backend/terraform.tfstate"
    region = "eu-west-2"
  }
}