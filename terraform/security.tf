resource "yandex_vpc_security_group" "bastion-sg" {
  network_id = yandex_vpc_network.production-net.id

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = ["95.24.75.10/32"]
    port = 22
  }

  ingress {
    protocol = "ICMP"
    v4_cidr_blocks = ["95.24.75.10/32"]
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
    protocol = "TCP"
    v4_cidr_blocks = ["198.18.235.0/24", "198.18.248.0/24"]
    port = 80
  }

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 80
  }

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 443
  }

  egress {
    protocol = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<EOT
[bastion]
bastion_host ansible_host=${yandex_compute_instance.bastion.network_interface[0].nat_ip_address}

[web_servers]
web_server_1 ansible_host=${yandex_compute_instance.web_servers[0].network_interface[0].ip_address}
web_server_2 ansible_host=${yandex_compute_instance.web_servers[1].network_interface[0].ip_address}
EOT
}
