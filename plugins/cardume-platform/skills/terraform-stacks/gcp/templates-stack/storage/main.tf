module "bucket" {
  source = "git@github.com:YOUR_ORG/terraform-modules.git//gcp/storage?ref=v1.0.0"

  project_id      = var.project_id
  name            = var.bucket_name
  location        = var.bucket_location
  storage_class   = var.storage_class
  versioning      = var.versioning
  kms_key_name    = var.kms_key_name
  lifecycle_rules = var.lifecycle_rules
  labels          = var.labels
}
