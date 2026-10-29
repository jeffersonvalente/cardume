output "bucket_name" {
  description = "Bucket name."
  value       = module.bucket.name
}

output "bucket_url" {
  description = "gs:// URL of the bucket."
  value       = module.bucket.url
}
