module "subnet" {
  source = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/subnet?ref=v1.0.0"

  project_id               = var.project_id
  region                   = var.region
  network                  = var.network_self_link
  name                     = var.subnet_name
  ip_cidr_range            = var.subnet_cidr
  secondary_ranges         = var.secondary_ranges
  private_ip_google_access = var.private_ip_google_access
  flow_logs                = var.flow_logs
  enable_nat               = var.enable_nat
  router_name              = var.router_name
  nat_name                 = var.nat_name
  nat_static_ip_names      = var.nat_static_ip_names
  nat_logging              = var.nat_logging
}
