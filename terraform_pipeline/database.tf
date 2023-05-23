# Create a RDS database
resource "aws_db_instance" "jet_db" {
  identifier             = "jet-db"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  username               = var.username
  password               = var.password
  publicly_accessible    = true
  db_subnet_group_name   = data.aws_db_subnet_group.c7-subnets.name
  vpc_security_group_ids = [data.aws_security_group.c7-remote-access.id]
  skip_final_snapshot    = true

  # Define two database schemas
  provisioner "local-exec" {
    command     = "psql -h ${aws_db_instance.jet_db.address} -p ${aws_db_instance.jet_db.port} -U ${var.username} -d postgres -f schema.sql"
    environment = {
      PGPASSWORD = var.password
    }
  }
}