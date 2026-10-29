variable "project_id" {
  description = "ID of the project that hosts the VM."
  type        = string
}

variable "name" {
  description = "Instance name."
  type        = string
}

variable "region" {
  description = "Region of the zone, used for the schedule policy."
  type        = string
}

variable "zone" {
  description = "Zone of the instance, for example us-central1-a."
  type        = string
}

variable "machine_type" {
  description = "Machine type, for example e2-medium."
  type        = string
}

variable "image" {
  description = "Boot image, for example debian-cloud/debian-12."
  type        = string
}

variable "disk_size_gb" {
  description = "Boot disk size in GB."
  type        = number
  default     = 20
}

variable "disk_type" {
  description = "Boot disk type: pd-standard, pd-balanced or pd-ssd."
  type        = string
  default     = "pd-balanced"
}

variable "kms_key_self_link" {
  description = "Cloud KMS key used to encrypt the boot disk (CMEK). The Compute Engine service agent needs roles/cloudkms.cryptoKeyEncrypterDecrypter on it."
  type        = string
}

variable "subnetwork" {
  description = "Self link of the subnet for the primary interface."
  type        = string
}

variable "external_ip" {
  description = "Attach an ephemeral external IP. Keep false and use IAP TCP forwarding or Cloud NAT where possible."
  type        = bool
  default     = false
}

variable "network_tags" {
  description = "Network tags used by firewall rules."
  type        = list(string)
  default     = []
}

variable "ssh_keys" {
  description = "Instance-level ssh-keys metadata, one USERNAME:KEY_TYPE KEY_VALUE COMMENT entry per line. Leave null to use OS Login instead."
  type        = string
  default     = null
}

variable "service_account_email" {
  description = "Dedicated service account the VM runs as."
  type        = string
}

variable "scopes" {
  description = "OAuth scopes. Keep cloud-platform and control access with IAM roles on the service account."
  type        = list(string)
  default     = ["https://www.googleapis.com/auth/cloud-platform"]
}

variable "startup_script" {
  description = "Script run on every boot."
  type        = string
  default     = null
}

variable "schedule" {
  description = "Optional start/stop schedule. Cron expressions in the given IANA time zone; start_cron may be omitted for stop-only schedules."
  type = object({
    stop_cron  = string
    start_cron = optional(string)
    time_zone  = string
  })
  default = null
}

variable "deletion_protection" {
  description = "Refuse deletion of the instance while true."
  type        = bool
  default     = false
}
