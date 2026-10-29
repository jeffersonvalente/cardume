resource "google_compute_network" "this" {
  project                         = var.project_id
  name                            = var.name
  description                     = var.description
  auto_create_subnetworks         = false
  routing_mode                    = var.routing_mode
  mtu                             = var.mtu
  delete_default_routes_on_create = var.delete_default_routes_on_create
}
