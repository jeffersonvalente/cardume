variable "project_id" {
  description = "ID of the Google Cloud project that owns the network."
  type        = string
}

variable "network" {
  description = "Name or self link of the VPC network the rule applies to."
  type        = string
}

variable "name" {
  description = "Firewall rule name."
  type        = string
}

variable "description" {
  description = "Why the rule exists. Reviewers read this first."
  type        = string
  default     = null
}

variable "priority" {
  description = "Rule priority from 0 (highest) to 65535."
  type        = number
  default     = 1000
}

variable "source_ranges" {
  description = "Source CIDR blocks allowed to connect, for example the IAP range 35.235.240.0/20."
  type        = list(string)
}

variable "target_tags" {
  description = "Network tags of the instances the rule targets. An empty list targets every instance in the network."
  type        = list(string)
  default     = []
}

variable "allow" {
  description = "Protocols and ports to allow, for example [{ protocol = \"tcp\", ports = [\"443\"] }]."
  type = list(object({
    protocol = string
    ports    = optional(list(string), [])
  }))
}

variable "logging" {
  description = "Record connections matched by this rule in Firewall Rules Logging."
  type        = bool
  default     = false
}

variable "allow_internet_source" {
  description = "Explicit opt-in for 0.0.0.0/0 in source_ranges."
  type        = bool
  default     = false
}
