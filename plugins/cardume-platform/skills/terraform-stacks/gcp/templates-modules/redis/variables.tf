variable "project_id" {
  description = "ID of the project that hosts the instance."
  type        = string
}

variable "name" {
  description = "Instance name."
  type        = string
}

variable "region" {
  description = "Region of the instance."
  type        = string
}

variable "tier" {
  description = "BASIC (single node) or STANDARD_HA (replicated with automatic failover)."
  type        = string
  default     = "STANDARD_HA"

  validation {
    condition     = contains(["BASIC", "STANDARD_HA"], var.tier)
    error_message = "tier must be BASIC or STANDARD_HA."
  }
}

variable "memory_size_gb" {
  description = "Memory capacity in GB."
  type        = number
}

variable "redis_version" {
  description = "Redis version, for example REDIS_7_2."
  type        = string
  default     = "REDIS_7_2"
}

variable "network" {
  description = "ID of the VPC network that clients connect from. It needs an existing private services access connection."
  type        = string
}

variable "reserved_ip_range" {
  description = "Name of the allocated range for private services access. Null lets Google pick one from the existing allocation."
  type        = string
  default     = null
}

variable "maintenance_day" {
  description = "Maintenance day, for example SUNDAY."
  type        = string
  default     = "SUNDAY"
}

variable "maintenance_hour" {
  description = "Maintenance start hour in UTC, 0 to 23."
  type        = number
  default     = 4
}
