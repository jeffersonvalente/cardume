terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 9.0"
    }
  }

  backend "gcs" {
    bucket = "YOUR_ORG-tfstate-ENV"
    prefix = "terraform/ENV/REGION/gke"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
