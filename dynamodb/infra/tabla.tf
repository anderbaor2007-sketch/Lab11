resource "aws_dynamodb_table" "telemetria" {
  name         = var.table_name
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

  attribute {
    name = "empresaId"
    type = "S"
  }


  global_secondary_index {
    name            = "empresa-timestamp-index"
    hash_key        = "empresaId"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

 
  ttl {
    attribute_name = "expiracion"
    enabled        = true
  }

 
  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Project = "TerraFleet"
    Lab     = "11"
    Service = "DynamoDB"
  }
}