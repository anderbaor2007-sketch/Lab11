output "cache_endpoint" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}

output "tabla_fuente" {
  value = aws_dynamodb_table.fuente.name
}

output "vpc_id" {
  value = aws_vpc.lab.id
}

output "lambdas" {
  value = { for k, f in aws_lambda_function.fn : k => f.function_name }
}
