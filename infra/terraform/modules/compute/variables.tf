variable "zone" {
  type    = string
  default = "ru-central1-a"
}

variable "name_prefix" {
  type    = string
  default = "devops"
}

variable "vms" {
  type = map(object({
    public_ip = bool
  }))
  description = "Map of VM name to config. public_ip controls static external IP."
}

variable "vm_user" {
  type    = string
  default = "ubuntu"
}

variable "ssh_pubkey" {
  type = string
}

variable "subnet_id" {
  type = string
}
