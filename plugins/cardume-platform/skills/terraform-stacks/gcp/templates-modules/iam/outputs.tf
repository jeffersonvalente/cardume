output "id" {
  description = "Full role name, for example projects/my-project/roles/logReader_role."
  value       = google_project_iam_custom_role.this.id
}

output "role_id" {
  description = "Short role ID."
  value       = google_project_iam_custom_role.this.role_id
}
