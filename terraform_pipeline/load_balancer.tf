data "aws_subnet_ids" "c7_subnets" {
  vpc_id = data.aws_vpc.c7-vpc.id
}

resource "aws_lb" "jet_load_balancer" {
    name = "jet-load-balancer"
    internal = false
    load_balancer_type = "application"
    security_groups = [data.aws_security_group.c7-remote-access.id]
    subnets = [
        "subnet-0bd43551b596597e1",
        "subnet-07f982f51c870f9d1",
        "subnet-0b265a90c0cadfb99"
    ]
}

resource "aws_lb_target_group" "jet_tg" {
    name = "jet-target-group"
    port = 80
    protocol = "HTTP"
    vpc_id = data.aws_vpc.c7-vpc.id
}

resource "aws_lb_target_group_attachment" "jet_tg_attachment" {
  target_group_arn = aws_lb_target_group.jet_tg.arn
  target_id = aws_instance.jet_instance.id
  port = 80
}
