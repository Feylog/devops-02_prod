output "vm_ip" {
  value = yandex_vpc_address.static_ip.external_ipv4_address[0].address
}

output "vm_id" {
  value = yandex_compute_instance.vm.id
}
