variable "zone" {
  type    = string
  default = "ru-central1-a"
}

variable "name_prefix" {
  type    = string
  default = "devops"
}

variable "vm_name" {
  type    = string
  default = "devops-vm"
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
