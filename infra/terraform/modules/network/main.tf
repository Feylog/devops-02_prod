resource "yandex_vpc_network" "net" {
  name = "${var.name_prefix}-net"
}

resource "yandex_vpc_gateway" "nat" {
  name = "${var.name_prefix}-nat-gw"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "rt" {
  name       = "${var.name_prefix}-rt"
  network_id = yandex_vpc_network.net.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.nat.id
  }
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "${var.name_prefix}-subnet-a"
  zone           = var.zone
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["10.10.0.0/24"]
  route_table_id = yandex_vpc_route_table.rt.id
}
