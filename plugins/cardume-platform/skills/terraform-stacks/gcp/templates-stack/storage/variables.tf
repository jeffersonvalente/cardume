variable "project_id" {
  description = "ID of the Google Cloud project the stack deploys into."
  type        = string
}

variable "region" {
  description = "Default region for the provider and regional resources."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique bucket name, ending in -bkt."
  type        = string
}

variable "bucket_location" {
  description = "Region, dual-region or multi-region of the bucket."
  type        = string
}

variable "storage_class" {
  description = "Default storage class."
  type        = string
  default     = "STANDARD"
}

variable "versioning" {
  description = "Keep noncurrent object versions."
  type        = bool
  default     = true
}

variable "kms_key_name" {
  description = "Cloud KMS key for CMEK, or null for Google-managed keys."
  type        = string
  default     = null
}

variable "lifecycle_rules" {
  description = "Lifecycle rules passed to the module. The default deletes objects 30 days after creation."
  type = list(object({
    action             = string
    storage_class      = optional(string)
    age                = optional(number)
    with_state         = optional(string)
    num_newer_versions = optional(number)
    matches_prefix     = optional(list(string))
  }))
  default = [
    {
      action = "Delete"
      age    = 30
    }
  ]
}

variable "labels" {
  description = "Cost allocation labels."
  type        = map(string)
  default     = {}
}
