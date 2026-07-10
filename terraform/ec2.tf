data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  associate_public_ip_address = true
  vpc_security_group_ids = [aws_security_group.allow_traffic.id]
  key_name               = "EC2_sprint"
  user_data              = <<-EOF
              #!/bin/bash
              EOF

  user_data_replace_on_change = true

  tags = {
    Name = "nc-plus-one"
  }
}

output "public_ip" {
  value = aws_instance.example.public_ip
}