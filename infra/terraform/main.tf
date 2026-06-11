terraform {
  required_version = ">= 1.5.0"
}

module "tenant_namespace" {
  source = "./modules/tenant-namespace"

  service_name = var.service_name
  team         = var.team
  environment  = var.environment
  namespace    = var.namespace
  labels       = var.labels
}
