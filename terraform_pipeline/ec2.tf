resource "aws_instance" "jet_instance" {
  ami="ami-0a242269c4b530c5e"
  key_name = "jet-key"
  instance_type = "t2.micro"
  subnet_id = "subnet-0bd43551b596597e1"
  vpc_security_group_ids = [data.aws_security_group.c7-remote-access.id]
  tags = {
    Name = "jet-instance"
  }
}
