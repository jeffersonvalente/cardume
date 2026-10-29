variable "project_id" {
  description = "ID of the project where the custom role is defined."
  type        = string
}

variable "role_id" {
  description = "Role ID. Letters, digits, underscores and periods only, 3 to 64 characters."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9_.]{3,64}$", var.role_id))
    error_message = "role_id accepts letters, digits, underscores and periods, 3 to 64 characters."
  }
}

variable "title" {
  description = "Human-readable role title."
  type        = string
}

variable "description" {
  description = "What the role is for and who should hold it."
  type        = string
  default     = null
}

variable "permissions" {
  description = "Exact permissions granted, for example storage.objects.get. Keep the list to what the workload calls."
  type        = list(string)

  validation {
    condition     = length(var.permissions) > 0
    error_message = "List at least one permission."
  }
}

variable "stage" {
  description = "Launch stage of the role: ALPHA, BETA, GA, DEPRECATED, DISABLED or EAP."
  type        = string
  default     = "GA"
}
