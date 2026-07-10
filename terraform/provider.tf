provider "aws" {
    region = "eu-west-2"
    default_tags {
        tags = {
        Owner       = "Gen"
        Project     = "nc-plus-one"
        }
    }
}