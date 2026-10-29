locals {
  router_name = coalesce(var.router_name, "${var.name}-rtr")
  nat_name    = coalesce(var.nat_name, "${var.name}-nat")
}

resource "google_compute_subnetwork" "this" {
  project                  = var.project_id
  name                     = var.name
  region                   = var.region
  network                  = var.network
  ip_cidr_range            = var.ip_cidr_range
  private_ip_google_access = var.private_ip_google_access

  dynamic "secondary_ip_range" {
    for_each = var.secondary_ranges
    content {
      range_name    = secondary_ip_range.key
      ip_cidr_range = secondary_ip_range.value
    }
  }

  dynamic "log_config" {
    for_each = var.flow_logs ? [1] : []
    content {
      aggregation_interval = "INTERVAL_5_SEC"
      flow_sampling        = var.flow_logs_sampling
      metadata             = "INCLUDE_ALL_METADATA"
    }
  }
}

resource "google_compute_router" "this" {
  count   = var.enable_nat ? 1 : 0
  project = var.project_id
  name    = local.router_name
  region  = var.region
  network = var.network
}

resource "google_compute_address" "nat" {
  for_each     = var.enable_nat ? toset(var.nat_static_ip_names) : toset([])
  project      = var.project_id
  name         = each.value
  region       = var.region
  address_type = "EXTERNAL"
}

resource "google_compute_router_nat" "this" {
  count                              = var.enable_nat ? 1 : 0
  project                            = var.project_id
  name                               = local.nat_name
  router                             = google_compute_router.this[0].name
  region                             = var.region
  nat_ip_allocate_option             = length(var.nat_static_ip_names) > 0 ? "MANUAL_ONLY" : "AUTO_ONLY"
  nat_ips                            = [for address in google_compute_address.nat : address.self_link]
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = google_compute_subnetwork.this.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }

  log_config {
    enable = var.nat_logging
    filter = var.nat_log_filter
  }
}
