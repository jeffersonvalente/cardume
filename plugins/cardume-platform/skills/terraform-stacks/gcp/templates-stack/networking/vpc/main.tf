module "vpc" {
  source = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/vpc?ref=v1.0.0"

  project_id   = var.project_id
  name         = var.network_name
  description  = var.network_description
  routing_mode = var.routing_mode
}
