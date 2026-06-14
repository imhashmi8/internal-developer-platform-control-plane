package idp.scorecard

default has_owner = false
default has_environment = false

has_owner {
  input.metadata.labels["idp.platform/team"]
}

has_environment {
  input.metadata.labels["idp.platform/environment"]
}

score := count([check | check := [has_owner, has_environment][_]; check])
