variable "project_id" {
  description = "ID of the Google Cloud project that owns the network."
  type        = string
}

variable "name" {
  description = "Network name. Lowercase letters, digits and hyphens, up to 63 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-z]([-a-z0-9]{0,61}[a-z0-9])?$", var.name))
    error_message = "The name must follow RFC 1035: start with a letter, use lowercase letters, digits or hyphens, and stay within 63 characters."
  }
}

variable "description" {
  description = "Free-text description shown in the console."
  type        = string
  default     = null
}

variable "routing_mode" {
  description = "Dynamic routing scope for Cloud Routers on this network: REGIONAL or GLOBAL."
  type        = string
  default     = "REGIONAL"

  validation {
    condition     = contains(["REGIONAL", "GLOBAL"], var.routing_mode)
    error_message = "routing_mode must be REGIONAL or GLOBAL."
  }
}

variable "mtu" {
  description = "Maximum transmission unit in bytes. 1460 is the Google Cloud default."
  type        = number
  default     = 1460
}

variable "delete_default_routes_on_create" {
  description = "Remove the default internet route right after the network is created. Use when egress must go through a firewall appliance or NAT you control."
  type        = bool
  default     = false
}
