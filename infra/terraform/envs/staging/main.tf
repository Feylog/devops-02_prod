module "network" {
  source      = "../../modules/network"
  zone        = var.zone
  name_prefix = "staging"
}

module "compute" {
  source      = "../../modules/compute"
  zone        = var.zone
  name_prefix = "staging"
  vm_name     = "staging-vm"
  vm_user     = var.vm_user
  ssh_pubkey  = var.ssh_pubkey
  subnet_id   = module.network.subnet_id
}
