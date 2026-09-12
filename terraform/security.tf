resource "yandex_vpc_security_group" "bastion-sg" {
  network_id = yandex_vpc_network.production-net.id

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = ["95.24.81.133/32"]
    port = 22
  }

  ingress {
    protocol = "ICMP"
    v4_cidr_blocks = ["95.24.81.133/32"]
  }

  egress {
    protocol = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "web-sg" {
  network_id = yandex_vpc_network.production-net.id

  ingress {
    protocol = "TCP"
    security_group_id = yandex_vpc_security_group.bastion-sg.id
    port = 22
  }

  ingress {
    protocol = "HTTP"
    v4_cidr_blocks = ["198.18.235.0/24", "198.18.248.0/24"]
    port = 80
  }

  ingress {
    protocol = "HTTP"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 80
  }

  ingress {
    protocol = "HTTPS"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 443
  }

  egress {
    protocol = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}