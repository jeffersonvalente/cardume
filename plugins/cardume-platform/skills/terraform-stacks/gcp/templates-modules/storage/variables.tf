variable "project_id" {
  description = "ID of the project that owns the bucket."
  type        = string
}

variable "name" {
  description = "Bucket name. Globally unique, 3 to 63 characters, lowercase letters, digits, hyphens, underscores and dots."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][-a-z0-9_.]{1,61}[a-z0-9]$", var.name)) && !startswith(var.name, "goog")
    error_message = "Bucket names use 3 to 63 lowercase letters, digits, hyphens, underscores or dots and cannot start with goog."
  }
}

variable "location" {
  description = "Region (us-central1), dual-region or multi-region (US, EU) of the bucket."
  type        = string
}

variable "storage_class" {
  description = "Default storage class: STANDARD, NEARLINE, COLDLINE or ARCHIVE."
  type        = string
  default     = "STANDARD"
}

variable "versioning" {
  description = "Keep noncurrent object versions after overwrite or delete."
  type        = bool
  default     = true
}

variable "kms_key_name" {
  description = "Cloud KMS key for default encryption (CMEK). Null keeps Google-managed keys. The Cloud Storage service agent needs encrypt/decrypt on the key."
  type        = string
  default     = null
}

variable "lifecycle_rules" {
  description = "Lifecycle rules. action is Delete, SetStorageClass or AbortIncompleteMultipartUpload; storage_class is required only for SetStorageClass."
  type = list(object({
    action             = string
    storage_class      = optional(string)
    age                = optional(number)
    with_state         = optional(string)
    num_newer_versions = optional(number)
    matches_prefix     = optional(list(string))
  }))
  default = []
}

variable "labels" {
  description = "Labels for cost allocation, for example { env = \"prd\", team = \"payments\" }."
  type        = map(string)
  default     = {}
}
