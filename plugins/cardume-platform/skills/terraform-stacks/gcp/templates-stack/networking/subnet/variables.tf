variable "project_id" {
  description = "ID of the Google Cloud project the stack deploys into."
  type        = string
}

variable "region" {
  description = "Default region for the provider and regional resources."
  type        = string
}

variable "network_self_link" {
  description = "Self link of the VPC created by the vpc stack."
  type        = string
}

variable "subnet_name" {
  description = "Subnet name, ending in the -snet suffix."
  type        = string
}

variable "subnet_cidr" {
  description = "Primary IPv4 range of the subnet."
  type        = string
}

variable "secondary_ranges" {
  description = "Secondary ranges keyed by name, for example GKE pods and services."
  type        = map(string)
  default     = {}
}

variable "private_ip_google_access" {
  description = "Let private VMs reach Google APIs."
  type        = bool
  default     = true
}

variable "flow_logs" {
  description = "Turn on VPC Flow Logs."
  type        = bool
  default     = false
}

variable "enable_nat" {
  description = "Create a Cloud Router and Cloud NAT for outbound internet access."
  type        = bool
  default     = true
}

variable "router_name" {
  description = "Cloud Router name, ending in -rtr."
  type        = string
  default     = null
}

variable "nat_name" {
  description = "Cloud NAT name, ending in -nat."
  type        = string
  default     = null
}

variable "nat_static_ip_names" {
  description = "Names of static egress IPs to reserve, each ending in -ip. Empty for automatic allocation."
  type        = list(string)
  default     = []
}

variable "nat_logging" {
  description = "Log NAT errors to Cloud Logging."
  type        = bool
  default     = true
}
