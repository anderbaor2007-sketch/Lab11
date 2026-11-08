resource "aws_elasticache_subnet_group" "this" {
  name       = "lab11-cache-subnets"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_parameter_group" "this" {
  name        = "lab11-valkey8"
  family      = "valkey8"
  description = "Politica de memoria del Lab 11"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id = "lab11-terrafleet"
  description          = "Cache de ultima posicion de la flota TerraFleet"

  engine         = "valkey"
  engine_version = "8.0"
  node_type      = var.node_type
  port           = 6379

  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled           = true

  subnet_group_name    = aws_elasticache_subnet_group.this.name
  security_group_ids   = [aws_security_group.cache.id]
  parameter_group_name = aws_elasticache_parameter_group.this.name

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  snapshot_retention_limit = 0
  apply_immediately        = true
}
