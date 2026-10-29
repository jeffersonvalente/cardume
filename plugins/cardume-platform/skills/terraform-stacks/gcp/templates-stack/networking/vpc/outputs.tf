output "network_id" {
  description = "Network ID."
  value       = module.vpc.id
}

output "network_name" {
  description = "Network name."
  value       = module.vpc.name
}

output "network_self_link" {
  description = "Network self link for subnet, firewall and GKE stacks."
  value       = module.vpc.self_link
}
