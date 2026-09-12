output "bastion_public_ip" {
  value = yandex_compute_instance.bastion.network_interface.nat_ip_address
}

output "web_private_ips" {
  value = yandex_compute_instance.web-servers.network_interface[*].ip_address
}

output "balancer_public_ip" {
  value = yandex_vpc_address.balancer_ip.external_ipv4_address[0].address
}