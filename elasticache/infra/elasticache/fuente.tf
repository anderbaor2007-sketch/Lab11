resource "aws_dynamodb_table" "fuente" {
  name         = "lab11-telemetria-fuente"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "equipoId"
  range_key    = "timestamp"

  attribute {
    name = "equipoId"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }
}
