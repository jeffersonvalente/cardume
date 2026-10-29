resource "google_container_node_pool" "this" {
  project  = var.project_id
  name     = var.name
  location = var.location
  cluster  = var.cluster

  autoscaling {
    min_node_count  = var.min_nodes
    max_node_count  = var.max_nodes
    location_policy = "BALANCED"
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = var.max_surge
    max_unavailable = 0
  }

  node_config {
    machine_type    = var.machine_type
    disk_size_gb    = var.disk_size_gb
    disk_type       = var.disk_type
    spot            = var.spot
    service_account = var.service_account_email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  lifecycle {
    precondition {
      condition     = var.min_nodes <= var.max_nodes
      error_message = "min_nodes cannot be greater than max_nodes."
    }
  }
}
