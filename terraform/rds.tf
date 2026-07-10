data "aws_secretsmanager_secret" "db" {
  name = "nc-plus-one-db"
}

data "aws_secretsmanager_secret_version" "db" {
  secret_id = data.aws_secretsmanager_secret.db.id
}

locals {
  db_credentials = jsondecode(
    data.aws_secretsmanager_secret_version.db.secret_string
  )
}

resource "aws_db_instance" "ncplusonedb" {
  allocated_storage    = 10
  db_name              = "ncplusone"
  engine               = "postgres"
  engine_version       = "14.18"
  instance_class       = "db.t3.micro"
  username             = local.db_credentials.username
  password             = local.db_credentials.password
  skip_final_snapshot  = true

  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
}

output "db_endpoint" {
  value = aws_db_instance.ncplusonedb.endpoint
}

output "db_port" {
  value = aws_db_instance.ncplusonedb.port
}