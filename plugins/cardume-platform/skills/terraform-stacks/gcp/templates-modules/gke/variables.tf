variable "project_id" {
  description = "ID of the project that hosts the cluster."
  type        = string
}

variable "name" {
  description = "Cluster name, up to 40 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z]([-a-z0-9]{0,38}[a-z0-9])?$", var.name))
    error_message = "Cluster names start with a letter, use lowercase letters, digits or hyphens, and stay within 40 characters."
  }
}

variable "location" {
  description = "A region for a regional (highly available) control plane, or a zone for a zonal one."
  type        = string
}

variable "network" {
  description = "Self link or name of the VPC network."
  type        = string
}

variable "subnetwork" {
  description = "Self link or name of the subnet the nodes use."
  type        = string
}

variable "release_channel" {
  description = "GKE release channel: RAPID, REGULAR, STABLE or EXTENDED."
  type        = string
  default     = "REGULAR"

  validation {
    condition     = contains(["RAPID", "REGULAR", "STABLE", "EXTENDED"], var.release_channel)
    error_message = "release_channel must be RAPID, REGULAR, STABLE or EXTENDED."
  }
}

variable "pods_range_name" {
  description = "Name of an existing secondary range on the subnet for pods. Takes precedence over pods_cidr."
  type        = string
  default     = null
}

variable "services_range_name" {
  description = "Name of an existing secondary range on the subnet for services. Takes precedence over services_cidr."
  type        = string
  default     = null
}

variable "pods_cidr" {
  description = "CIDR for pods when no secondary range name is given, for example 10.20.0.0/16."
  type        = string
  default     = null
}

variable "services_cidr" {
  description = "CIDR for services when no secondary range name is given, for example 10.30.0.0/20."
  type        = string
  default     = null
}

variable "private_nodes" {
  description = "Give nodes internal IPs only. Pair with Cloud NAT for outbound traffic."
  type        = bool
  default     = true
}

variable "private_endpoint" {
  description = "Expose the control plane on its internal IP only. Requires a path into the VPC (VPN, Interconnect or a bastion)."
  type        = bool
  default     = false
}

variable "master_cidr" {
  description = "A /28 range for the control plane when private_nodes is true, for example 172.16.0.0/28."
  type        = string
  default     = null
}

variable "authorized_networks" {
  description = "CIDR blocks allowed to reach the control plane endpoint."
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

variable "deletion_protection" {
  description = "Block terraform destroy and replacement of the cluster until this is set to false and applied."
  type        = bool
  default     = true
}
