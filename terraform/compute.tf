data "yandex_compute_image" "ubuntu_24" {
  family = "ubuntu-2404-lts"
}

resource "yandex_compute_instance" "bastion" {
  name = "prod-bastion"
  zone = var.yc_zone

  resources {
    cores = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu_24.id
      size = 20
      type = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.public-subnet.id
    nat = true
    security_group_ids = [yandex_vpc_security_group.bastion-sg.id]
  }

  metadata = {
    user-data = file("${path.module}/cloud-init.yaml")
  }
}

resource "yandex_compute_instance" "web_servers" {
  count = 2
  name = "prod-web-${count.index + 1}"

  zone = var.yc_zone

  resources {
    cores = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu_24.id
      size = 20
      type = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.private-subnet.id
    nat = false
    security_group_ids = [yandex_vpc_security_group.web-sg.id]
  }

  metadata = {
    user-data = file("${path.module}/cloud-init.yaml")
  }
}