# Un rol por Lambda, con el permiso minimo que necesita (sin comodines).
locals {
  funciones = {
    poblador = {
      handler  = "poblador.main"
      timeout  = 120
      acciones = ["dynamodb:PutItem", "dynamodb:BatchWriteItem"]
    }
    consultar = {
      handler  = "consultar.main"
      timeout  = 60
      acciones = ["dynamodb:Query", "dynamodb:GetItem"]
    }
    geocerca = {
      handler  = "geocerca.main"
      timeout  = 30
      acciones = []
    }
    benchmark = {
      handler  = "benchmark.main"
      timeout  = 120
      acciones = ["dynamodb:Query", "dynamodb:GetItem"]
    }
  }

  funciones_con_dynamodb = {
    for k, v in local.funciones : k => v if length(v.acciones) > 0
  }
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "fn" {
  for_each           = local.funciones
  name               = "lab11-${each.key}"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# Permite crear interfaces de red en la VPC y escribir logs en CloudWatch.
resource "aws_iam_role_policy_attachment" "vpc" {
  for_each   = local.funciones
  role       = aws_iam_role.fn[each.key].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "dynamodb" {
  for_each = local.funciones_con_dynamodb
  name     = "dynamodb-fuente"
  role     = aws_iam_role.fn[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = each.value.acciones
      Resource = aws_dynamodb_table.fuente.arn
    }]
  })
}
