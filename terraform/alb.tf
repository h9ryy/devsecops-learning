resource "yandex_alb_target_group" "web-targets" {
  name = "web-target-group-v2"

  dynamic "target" {
    for_each = yandex_compute_instance.web_servers

    content {
      subnet_id = yandex_vpc_subnet.private-subnet.id
      ip_address = target.value.network_interface[0].ip_address
    }
  }
}

resource "yandex_alb_backend_group" "web-backend-group" {
  name = "prod-web-backend-group-v2"
    
  http_backend {
    name = "http-backend"
    port = 80
    target_group_ids = [yandex_alb_target_group.web-targets.id]
        
    healthcheck {
      interval = "2s"
      timeout = "1s"
      http_healthcheck {
        path = "/"
      }
    }
  }
}

resource "yandex_alb_http_router" "web-router" {
  name = "prod-web-router-v2"
}

resource "yandex_alb_virtual_host" "web-virtual-host" {
  name = "prod-web-virtual-host"
  http_router_id = yandex_alb_http_router.web-router.id

  route {
    name = "main-route"
    http_route {
      http_route_action {
        backend_group_id = yandex_alb_backend_group.web-backend-group.id
        timeout = "60s"
      }
    }
  }
}

resource "yandex_alb_load_balancer" "app-balancer" {
  name = "prod-web-balancer"
  network_id = yandex_vpc_network.production-net.id
  security_group_ids = [yandex_vpc_security_group.alg-sg.id]

  allocation_policy {
    location {
      zone_id = var.yc_zone
      subnet_id = yandex_vpc_subnet.public-subnet.id
    }
  }

  listener {
    name = "http-listener"
    endpoint {
      ports = [80] 
      address {
        external_ipv4_address {
          address = yandex_vpc_address.balancer_ip.external_ipv4_address[0].address
        }
      }
    }
    http {
      handler {
        http_router_id = yandex_alb_http_router.web-router.id
      }
    }
  }
}