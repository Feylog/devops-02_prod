module "network" {
  source      = "../../modules/network"
  zone        = var.zone
  name_prefix = "prod"
}

module "compute" {
  source      = "../../modules/compute"
  zone        = var.zone
  name_prefix = "prod"
  vms = {
    "control-plane" = { public_ip = true }
    "worker-1"      = { public_ip = false }
    "worker-2"      = { public_ip = false }
  }
  vm_user     = var.vm_user
  ssh_pubkey  = var.ssh_pubkey
  subnet_id   = module.network.subnet_id
}
