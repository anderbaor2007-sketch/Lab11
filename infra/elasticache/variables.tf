variable "region" {
  description = "Region de AWS (el profesor exige Ohio)"
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "Perfil de la AWS CLI"
  type        = string
  default     = "lab11"
}

variable "node_type" {
  description = "Tipo de nodo de ElastiCache"
  type        = string
  default     = "cache.t4g.micro"
}

variable "cache_ttl_s" {
  description = "TTL (segundos) de las claves equipo:*:pos en el cache. Se varia en E2."
  type        = number
  default     = 10
}
