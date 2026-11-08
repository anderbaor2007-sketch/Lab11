
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


resource "aws_iam_role" "procesar_telemetria" {
  name               = "lab11-dynamo-procesar-telemetria"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "procesar_logs" {
  role       = aws_iam_role.procesar_telemetria.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "procesar_dynamo" {
  name = "lab11-procesar-dynamo-write"
  role = aws_iam_role.procesar_telemetria.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:PutItem", "dynamodb:BatchWriteItem"]
      Resource = aws_dynamodb_table.telemetria.arn
    }]
  })
}


resource "aws_iam_role" "consultar_telemetria" {
  name               = "lab11-dynamo-consultar-telemetria"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "consultar_logs" {
  role       = aws_iam_role.consultar_telemetria.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "consultar_dynamo" {
  name = "lab11-consultar-dynamo-read"
  role = aws_iam_role.consultar_telemetria.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:Query"]
      Resource = [
        aws_dynamodb_table.telemetria.arn,
        "${aws_dynamodb_table.telemetria.arn}/index/*"
      ]
    }]
  })
}


resource "aws_iam_role" "benchmark" {
  name               = "lab11-dynamo-benchmark"
  assume_role_policy  = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy_attachment" "benchmark_logs" {
  role       = aws_iam_role.benchmark.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "benchmark_dynamo" {
  name = "lab11-benchmark-dynamo-read"
  role = aws_iam_role.benchmark.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:GetItem", "dynamodb:Query"]
      Resource = [
        aws_dynamodb_table.telemetria.arn,
        "${aws_dynamodb_table.telemetria.arn}/index/*"
      ]
    }]
  })
}