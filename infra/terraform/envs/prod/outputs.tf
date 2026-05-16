output "prod_public_ips" {
  value = module.compute.vm_public_ips
}

output "prod_internal_ips" {
  value = module.compute.vm_internal_ips
}
