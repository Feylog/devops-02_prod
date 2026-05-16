locals {
  vms_with_public_ip = {
    for name, cfg in var.vms : name => cfg if cfg.public_ip
  }
}

resource "yandex_vpc_address" "static_ip" {
  for_each = local.vms_with_public_ip
  name     = "${var.name_prefix}-${each.key}-ip"

  external_ipv4_address {
    zone_id = var.zone
  }
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_compute_instance" "vm" {
  for_each    = var.vms
  name        = "${var.name_prefix}-${each.key}"
  platform_id = "standard-v3"
  zone        = var.zone

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 20
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id      = var.subnet_id
    nat            = each.value.public_ip
    nat_ip_address = each.value.public_ip ? yandex_vpc_address.static_ip[each.key].external_ipv4_address[0].address : null
  }

  metadata = {
    ssh-keys = "${var.vm_user}:${var.ssh_pubkey}"
  }
}
