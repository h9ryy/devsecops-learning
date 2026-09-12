resource "yandex_vpc_network" "production-net" {
  name = "secure-network"
}

resource "yandex_vpc_subnet" "private-subnet" {
  name = "private-sub"
  zone = var.yc_zone
  network_id = yandex_vpc_network.production-net.id
  v4_cidr_blocks = ["10.10.10.0/24"]
  route_table_id = yandex_vpc_route_table.private-rt.id
}   

resource "yandex_vpc_subnet" "public-subnet" {
  name = "public-sub"
  zone = var.yc_zone
  network_id = yandex_vpc_network.production-net.id
  v4_cidr_blocks = ["10.10.11.0/24"]
}   

resource "yandex_vpc_address" "balancer_ip" {
  name = "alb-static-ip"
  external_ipv4_address {}
}

resource "yandex_vpc_gateway" "nat-gw" {
  name = "secure-nat-gateway"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "private-rt" {
  name = "prod-private-rt"
  network_id = yandex_vpc_network.production-net.id
  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id = yandex_vpc_gateway.nat-gw.id
  }
}