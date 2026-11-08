
resource "aws_lambda_function" "procesar_telemetria" {
  function_name    = "lab11-dynamo-procesar-telemetria"
  runtime          = "python3.12"
  handler          = "handler.main"
  role             = aws_iam_role.procesar_telemetria.arn
  filename         = "${path.module}/procesar_telemetria.zip"
  source_code_hash = filebase64sha256("${path.module}/procesar_telemetria.zip")
  timeout          = 60
  memory_size      = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.telemetria.name
      TTL_DAYS   = var.ttl_days
    }
  }

  tags = {
    Project = "TerraFleet"
    Lab     = "11"
  }
}


resource "aws_lambda_function" "consultar_telemetria" {
  function_name    = "lab11-dynamo-consultar-telemetria"
  runtime          = "python3.12"
  handler          = "handler.main"
  role             = aws_iam_role.consultar_telemetria.arn
  filename         = "${path.module}/consultar_telemetria.zip"
  source_code_hash = filebase64sha256("${path.module}/consultar_telemetria.zip")
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.telemetria.name
    }
  }

  tags = {
    Project = "TerraFleet"
    Lab     = "11"
  }
}


resource "aws_lambda_function" "benchmark" {
  function_name    = "lab11-dynamo-benchmark"
  runtime          = "python3.12"
  handler          = "handler.main"
  role             = aws_iam_role.benchmark.arn
  filename         = "${path.module}/benchmark.zip"
  source_code_hash = filebase64sha256("${path.module}/benchmark.zip")
  timeout          = 120
  memory_size      = 512

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.telemetria.name
    }
  }

  tags = {
    Project = "TerraFleet"
    Lab     = "11"
  }
}