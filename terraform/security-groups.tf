data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

resource "aws_security_group" "allow_traffic" {
  name        = "allow_traffic"
  description = "Allow SSH & HTTP inbound traffic and all outbound traffic"


  tags = {
    Name = "allow_traffic"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh_ingress" {
  security_group_id = aws_security_group.allow_traffic.id
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  cidr_ipv4         = "${chomp(data.http.myip.response_body)}/32"
}

resource "aws_vpc_security_group_egress_rule" "allow_ssh_egress" {
  security_group_id = aws_security_group.allow_traffic.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "allow_http" {
  security_group_id = aws_security_group.allow_traffic.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 8000
  to_port           = 8000
  ip_protocol       = "tcp"
}

resource "aws_security_group" "rds" {
  name        = "rds"
  description = "Allow inbound PostgreSQL traffic from the EC2 security group"
}

resource "aws_vpc_security_group_ingress_rule" "allow_postgresql_ingress" {
  security_group_id = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.allow_traffic.id

  from_port         = 5432
  to_port           = 5432
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "allow_postgresql_egress" {
  security_group_id = aws_security_group.rds.id

  ip_protocol = "-1"
  cidr_ipv4   = "0.0.0.0/0"
}