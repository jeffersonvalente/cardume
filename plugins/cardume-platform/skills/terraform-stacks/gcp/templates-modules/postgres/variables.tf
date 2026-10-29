variable "project_id" {
  description = "ID of the project that hosts the instance."
  type        = string
}

variable "name" {
  description = "Instance name. Cloud SQL reserves a deleted name for about a week, so pick names you will not need to reuse right away."
  type        = string
}

variable "region" {
  description = "Region of the instance."
  type        = string
}

variable "database_version" {
  description = "PostgreSQL major version, for example POSTGRES_16."
  type        = string
  default     = "POSTGRES_16"
}

variable "edition" {
  description = "Cloud SQL edition: ENTERPRISE or ENTERPRISE_PLUS. The tier must match the edition."
  type        = string
  default     = "ENTERPRISE"

  validation {
    condition     = contains(["ENTERPRISE", "ENTERPRISE_PLUS"], var.edition)
    error_message = "edition must be ENTERPRISE or ENTERPRISE_PLUS."
  }
}

variable "tier" {
  description = "Machine tier, for example db-custom-2-7680 (Enterprise) or db-perf-optimized-N-2 (Enterprise Plus)."
  type        = string
}

variable "high_availability" {
  description = "Run a standby in a second zone (REGIONAL availability)."
  type        = bool
  default     = true
}

variable "backup_start_time" {
  description = "Daily backup window start, HH:MM in UTC."
  type        = string
  default     = "03:00"
}

variable "retained_backups" {
  description = "Number of automated backups to keep."
  type        = number
  default     = 14
}

variable "point_in_time_recovery" {
  description = "Keep transaction logs for point-in-time recovery."
  type        = bool
  default     = true
}

variable "psc_allowed_consumer_projects" {
  description = "Projects allowed to create Private Service Connect endpoints to this instance."
  type        = list(string)
}

variable "maintenance_day" {
  description = "Maintenance day, 1 (Monday) to 7 (Sunday)."
  type        = number
  default     = 7
}

variable "maintenance_hour" {
  description = "Maintenance hour in UTC, 0 to 23."
  type        = number
  default     = 4
}

variable "deletion_protection" {
  description = "Protect the instance from deletion both in Terraform and in the Cloud SQL API."
  type        = bool
  default     = true
}
