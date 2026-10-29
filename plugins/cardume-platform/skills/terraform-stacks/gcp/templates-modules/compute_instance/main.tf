locals {
  oslogin_metadata = tomap({ "enable-oslogin" = "TRUE" })
  ssh_key_metadata = tomap({ "enable-oslogin" = "FALSE", "ssh-keys" = var.ssh_keys })
  metadata         = var.ssh_keys == null ? local.oslogin_metadata : local.ssh_key_metadata
}

resource "google_compute_resource_policy" "schedule" {
  count   = var.schedule == null ? 0 : 1
  project = var.project_id
  name    = "${var.name}-sched"
  region  = var.region

  instance_schedule_policy {
    time_zone = var.schedule.time_zone

    vm_stop_schedule {
      schedule = var.schedule.stop_cron
    }

    dynamic "vm_start_schedule" {
      for_each = var.schedule.start_cron == null ? [] : [var.schedule.start_cron]
      content {
        schedule = vm_start_schedule.value
      }
    }
  }
}

resource "google_compute_instance" "this" {
  project                   = var.project_id
  name                      = var.name
  zone                      = var.zone
  machine_type              = var.machine_type
  tags                      = var.network_tags
  deletion_protection       = var.deletion_protection
  allow_stopping_for_update = true
  metadata_startup_script   = var.startup_script
  resource_policies         = google_compute_resource_policy.schedule[*].id

  metadata = local.metadata

  boot_disk {
    kms_key_self_link = var.kms_key_self_link

    initialize_params {
      image = var.image
      size  = var.disk_size_gb
      type  = var.disk_type
    }
  }

  network_interface {
    subnetwork = var.subnetwork

    dynamic "access_config" {
      for_each = var.external_ip ? [1] : []
      content {}
    }
  }

  service_account {
    email  = var.service_account_email
    scopes = var.scopes
  }

  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
}
