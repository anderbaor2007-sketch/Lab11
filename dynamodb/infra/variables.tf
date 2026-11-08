

variable "region" {
  description = "Región de AWS"
  default     = "us-east-2"
}

variable "table_name" {
  description = "Nombre de la tabla DynamoDB de telemetría"
  default     = "lab11-telemetria"
}

variable "ttl_days" {
  description = "Días antes de que DynamoDB elimine un registro por TTL"
  default     = 7
}