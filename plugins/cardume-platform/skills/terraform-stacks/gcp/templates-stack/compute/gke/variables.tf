variable "project_id" {
  description = "ID of the Google Cloud project the stack deploys into."
  type        = string
}

variable "region" {
  description = "Default region for the provider and regional resources."
  type        = string
}

variable "network_self_link" {
  description = "Self link of the VPC network."
  type        = string
}

variable "subnet_self_link" {
  description = "Self link of the subnet for the nodes."
  type        = string
}

variable "cluster_name" {
  description = "Cluster name, ending in -gke, at most 40 characters."
  type        = string
}

variable "release_channel" {
  description = "RAPID, REGULAR, STABLE or EXTENDED."
  type        = string
  default     = "REGULAR"
}

variable "pods_range_name" {
  description = "Subnet secondary range used for pods."
  type        = string
}

variable "services_range_name" {
  description = "Subnet secondary range used for services."
  type        = string
}

variable "private_nodes" {
  description = "Nodes get internal IPs only."
  type        = bool
  default     = true
}

variable "private_endpoint" {
  description = "Control plane reachable only from inside the VPC."
  type        = bool
  default     = false
}

variable "master_cidr" {
  description = "A /28 for the control plane, unused elsewhere in the VPC."
  type        = string
}

variable "authorized_networks" {
  description = "CIDR blocks allowed to reach the control plane."
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

variable "deletion_protection" {
  description = "Block deletion of the cluster."
  type        = bool
  default     = true
}

variable "node_pool_name" {
  description = "Node pool name, ending in -np."
  type        = string
}

variable "machine_type" {
  description = "Node machine type."
  type        = string
}

variable "min_nodes" {
  description = "Minimum nodes per zone."
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum nodes per zone."
  type        = number
  default     = 3
}

variable "spot" {
  description = "Use Spot VMs for the pool."
  type        = bool
  default     = false
}

variable "node_service_account_email" {
  description = "Dedicated service account for the nodes."
  type        = string
}
