output "vm_public_ips" {
  value = {
    for name in keys(yandex_vpc_address.static_ip) :
    name => yandex_vpc_address.static_ip[name].external_ipv4_address[0].address
  }
}

output "vm_internal_ips" {
  value = {
    for name, vm in yandex_compute_instance.vm :
    name => vm.network_interface[0].ip_address
  }
}
