output "staging_public_ips" {
  value = module.compute.vm_public_ips
}

output "staging_internal_ips" {
  value = module.compute.vm_internal_ips
}
