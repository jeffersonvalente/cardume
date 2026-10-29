resource "google_compute_firewall" "this" {
  project       = var.project_id
  name          = var.name
  description   = var.description
  network       = var.network
  direction     = "INGRESS"
  priority      = var.priority
  source_ranges = var.source_ranges
  target_tags   = var.target_tags

  dynamic "allow" {
    for_each = var.allow
    content {
      protocol = allow.value.protocol
      ports    = allow.value.ports
    }
  }

  dynamic "log_config" {
    for_each = var.logging ? [1] : []
    content {
      metadata = "INCLUDE_ALL_METADATA"
    }
  }

  lifecycle {
    precondition {
      condition     = var.allow_internet_source || !contains(var.source_ranges, "0.0.0.0/0")
      error_message = "0.0.0.0/0 opens the rule to the whole internet. Narrow source_ranges or set allow_internet_source = true on purpose."
    }
  }
}
