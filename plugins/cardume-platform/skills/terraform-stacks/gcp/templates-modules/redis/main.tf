resource "google_redis_instance" "this" {
  project                 = var.project_id
  name                    = var.name
  region                  = var.region
  tier                    = var.tier
  memory_size_gb          = var.memory_size_gb
  redis_version           = var.redis_version
  authorized_network      = var.network
  connect_mode            = "PRIVATE_SERVICE_ACCESS"
  reserved_ip_range       = var.reserved_ip_range
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  auth_enabled            = true

  maintenance_policy {
    weekly_maintenance_window {
      day = var.maintenance_day

      start_time {
        hours   = var.maintenance_hour
        minutes = 0
      }
    }
  }
}
