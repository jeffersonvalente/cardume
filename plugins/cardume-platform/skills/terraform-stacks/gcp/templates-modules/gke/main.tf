resource "google_container_cluster" "this" {
  project                  = var.project_id
  name                     = var.name
  location                 = var.location
  network                  = var.network
  subnetwork               = var.subnetwork
  networking_mode          = "VPC_NATIVE"
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = var.deletion_protection

  release_channel {
    channel = var.release_channel
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
    cluster_ipv4_cidr_block       = var.pods_range_name == null ? var.pods_cidr : null
    services_ipv4_cidr_block      = var.services_range_name == null ? var.services_cidr : null
  }

  dynamic "private_cluster_config" {
    for_each = var.private_nodes ? [1] : []
    content {
      enable_private_nodes    = true
      enable_private_endpoint = var.private_endpoint
      master_ipv4_cidr_block  = var.master_cidr
    }
  }

  dynamic "master_authorized_networks_config" {
    for_each = length(var.authorized_networks) > 0 ? [1] : []
    content {
      dynamic "cidr_blocks" {
        for_each = var.authorized_networks
        content {
          cidr_block   = cidr_blocks.value.cidr_block
          display_name = cidr_blocks.value.display_name
        }
      }
    }
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  lifecycle {
    precondition {
      condition     = !var.private_nodes || var.master_cidr != null
      error_message = "Private nodes need a /28 master_cidr for the control plane."
    }
  }
}
