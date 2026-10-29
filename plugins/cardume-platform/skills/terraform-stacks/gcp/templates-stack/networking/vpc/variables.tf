variable "project_id" {
  description = "ID of the Google Cloud project the stack deploys into."
  type        = string
}

variable "region" {
  description = "Default region for the provider and regional resources."
  type        = string
}

variable "network_name" {
  description = "Network name, ending in the -vpc suffix."
  type        = string
}

variable "network_description" {
  description = "What the network is for."
  type        = string
  default     = null
}

variable "routing_mode" {
  description = "REGIONAL or GLOBAL dynamic routing."
  type        = string
  default     = "REGIONAL"
}
