variable "project_id" {
  description = "ID of the project that hosts the cluster."
  type        = string
}

variable "name" {
  description = "Node pool name."
  type        = string
}

variable "location" {
  description = "Location of the parent cluster (region or zone)."
  type        = string
}

variable "cluster" {
  description = "Name of the parent cluster."
  type        = string
}

variable "machine_type" {
  description = "Compute Engine machine type for the nodes, for example e2-standard-4."
  type        = string
}

variable "min_nodes" {
  description = "Minimum nodes per zone for the autoscaler."
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum nodes per zone for the autoscaler."
  type        = number
  default     = 3
}

variable "max_surge" {
  description = "Extra nodes created during a surge upgrade."
  type        = number
  default     = 1
}

variable "disk_size_gb" {
  description = "Boot disk size per node in GB."
  type        = number
  default     = 100
}

variable "disk_type" {
  description = "Boot disk type: pd-standard, pd-balanced or pd-ssd."
  type        = string
  default     = "pd-balanced"
}

variable "spot" {
  description = "Use Spot VMs. Cheaper, but nodes can be reclaimed at any time."
  type        = bool
  default     = false
}

variable "service_account_email" {
  description = "Dedicated, minimally privileged service account for the nodes. Avoid the Compute Engine default account."
  type        = string
}
