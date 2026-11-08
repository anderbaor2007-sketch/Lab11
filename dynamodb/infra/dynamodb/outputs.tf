output "table_name" {
  value = aws_dynamodb_table.telemetria.name
}

output "table_arn" {
  value = aws_dynamodb_table.telemetria.arn
}

output "gsi_name" {
  value = "empresa-timestamp-index"
}

output "lambda_procesar" {
  value = aws_lambda_function.procesar_telemetria.function_name
}

output "lambda_consultar" {
  value = aws_lambda_function.consultar_telemetria.function_name
}

output "lambda_benchmark" {
  value = aws_lambda_function.benchmark.function_name
}