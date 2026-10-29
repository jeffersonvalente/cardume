module "cluster" {
  source = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/gke?ref=v1.0.0"

  project_id          = var.project_id
  name                = var.cluster_name
  location            = var.region
  network             = var.network_self_link
  subnetwork          = var.subnet_self_link
  release_channel     = var.release_channel
  pods_range_name     = var.pods_range_name
  services_range_name = var.services_range_name
  private_nodes       = var.private_nodes
  private_endpoint    = var.private_endpoint
  master_cidr         = var.master_cidr
  authorized_networks = var.authorized_networks
  deletion_protection = var.deletion_protection
}

module "node_pool" {
  source = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/nodepool?ref=v1.0.0"

  project_id            = var.project_id
  name                  = var.node_pool_name
  location              = var.region
  cluster               = module.cluster.name
  machine_type          = var.machine_type
  min_nodes             = var.min_nodes
  max_nodes             = var.max_nodes
  spot                  = var.spot
  service_account_email = var.node_service_account_email
}
