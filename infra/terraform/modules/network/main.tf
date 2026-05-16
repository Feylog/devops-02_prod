resource "yandex_vpc_network" "net" {
  name = "${var.name_prefix}-net"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "${var.name_prefix}-subnet-a"
  zone           = var.zone
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["10.10.0.0/24"]
}
