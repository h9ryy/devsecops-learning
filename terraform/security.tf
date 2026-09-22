data "http" "my_public_ip" {
  url = "https://icanhazip.com"
}

resource "yandex_vpc_security_group" "bastion-sg" {
  network_id = yandex_vpc_network.production-net.id

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = ["${chomp(data.http.my_public_ip.response_body)}/32"]
    port = 22
  }

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = yandex_vpc_subnet.private-subnet.v4_cidr_blocks
    from_port = 0
    to_port = 65535
  }

  ingress {
    protocol = "ICMP"
    v4_cidr_blocks = ["95.24.75.84/32"]
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
    security_group_id = yandex_vpc_security_group.alg-sg.id
    port = 80
  }

  ingress {
    protocol = "TCP"
    v4_cidr_blocks = yandex_vpc_subnet.private-subnet.v4_cidr_blocks
    from_port = 0
    to_port = 65535
  }

  egress {
    protocol = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "alg-sg" {
  network_id = yandex_vpc_network.production-net.id

  ingress {
    protocol = "TCP"
    description = "Allow HTTP"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 80
  }

  ingress {
    protocol = "TCP"
    description = "Allow HTTPS"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port = 443
  }

  egress {
    protocol = "ANY"
    description = "Allow all outgoing traffic"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<EOT
[bastion]
bastion_host ansible_host=${yandex_compute_instance.bastion.network_interface[0].nat_ip_address}

[web_monitoring]
web_server_1 ansible_host=${yandex_compute_instance.web_servers[0].network_interface[0].ip_address} ansible_ssh_common_args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p ubuntu@${yandex_compute_instance.bastion.network_interface[0].nat_ip_address}'"

[security_audit]
web_server_2 ansible_host=${yandex_compute_instance.web_servers[1].network_interface[0].ip_address} ansible_ssh_common_args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ProxyCommand='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -W %h:%p ubuntu@${yandex_compute_instance.bastion.network_interface[0].nat_ip_address}'"
EOT
}
