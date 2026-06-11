locals {
  service_account_name = "${var.service_name}-runtime"
}

resource "null_resource" "namespace_contract" {
  triggers = {
    namespace   = var.namespace
    service     = var.service_name
    team        = var.team
    environment = var.environment
    labels      = jsonencode(var.labels)
  }
}
