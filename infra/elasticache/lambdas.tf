# Las 4 Lambdas comparten un mismo zip (codigo + libreria redis + flota.json).
# El zip se arma antes con scripts\build_lambdas.ps1.
data "archive_file" "codigo" {
  type        = "zip"
  source_dir  = "${path.module}/../../app/elasticache/build"
  output_path = "${path.module}/codigo.zip"
}

resource "aws_lambda_function" "fn" {
  for_each = local.funciones

  function_name    = "lab11-${each.key}"
  role             = aws_iam_role.fn[each.key].arn
  runtime          = "python3.12"
  handler          = each.value.handler
  filename         = data.archive_file.codigo.output_path
  source_code_hash = data.archive_file.codigo.output_base64sha256
  timeout          = each.value.timeout
  memory_size      = 512

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      CACHE_HOST  = aws_elasticache_replication_group.this.primary_endpoint_address
      TABLE_NAME  = aws_dynamodb_table.fuente.name
      CACHE_TTL_S = tostring(var.cache_ttl_s)
    }
  }

  depends_on = [aws_iam_role_policy_attachment.vpc]
}
