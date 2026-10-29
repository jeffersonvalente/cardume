variable "project_id" {
  description = "ID of the Google Cloud project that owns the subnet."
  type        = string
}

variable "region" {
  description = "Region of the subnet, router and NAT, for example us-central1."
  type        = string
}

variable "network" {
  description = "Self link or ID of the parent VPC network."
  type        = string
}

variable "name" {
  description = "Subnet name. Also the base for the router and NAT names when those are not set."
  type        = string
}

variable "ip_cidr_range" {
  description = "Primary IPv4 range of the subnet, for example 10.10.0.0/20."
  type        = string

  validation {
    condition     = can(cidrhost(var.ip_cidr_range, 0))
    error_message = "ip_cidr_range must be a valid CIDR block."
  }
}

variable "secondary_ranges" {
  description = "Secondary ranges keyed by range name, for example GKE pods and services."
  type        = map(string)
  default     = {}
}

variable "private_ip_google_access" {
  description = "Let VMs without external IPs reach Google APIs."
  type        = bool
  default     = true
}

variable "flow_logs" {
  description = "Turn on VPC Flow Logs for the subnet."
  type        = bool
  default     = false
}

variable "flow_logs_sampling" {
  description = "Fraction of flows to sample when flow logs are on, between 0 and 1."
  type        = number
  default     = 0.5
}

variable "enable_nat" {
  description = "Create a Cloud Router and Cloud NAT so private VMs in this subnet get outbound internet access."
  type        = bool
  default     = false
}

variable "router_name" {
  description = "Cloud Router name. Defaults to the subnet name with an -rtr suffix."
  type        = string
  default     = null
}

variable "nat_name" {
  description = "Cloud NAT name. Defaults to the subnet name with a -nat suffix."
  type        = string
  default     = null
}

variable "nat_static_ip_names" {
  description = "Names of regional static external IPs to reserve for NAT. Leave empty to let Google allocate addresses automatically."
  type        = list(string)
  default     = []
}

variable "nat_logging" {
  description = "Send Cloud NAT logs to Cloud Logging."
  type        = bool
  default     = true
}

variable "nat_log_filter" {
  description = "Which NAT events to log: ERRORS_ONLY, TRANSLATIONS_ONLY or ALL."
  type        = string
  default     = "ERRORS_ONLY"

  validation {
    condition     = contains(["ERRORS_ONLY", "TRANSLATIONS_ONLY", "ALL"], var.nat_log_filter)
    error_message = "nat_log_filter must be ERRORS_ONLY, TRANSLATIONS_ONLY or ALL."
  }
}
