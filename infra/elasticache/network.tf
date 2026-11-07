# Red del laboratorio: VPC propia, 2 subredes privadas en 2 zonas, sin NAT.
data "aws_availability_zones" "az" {
  state = "available"
}

resource "aws_vpc" "lab" {
  cidr_block           = "10.11.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "lab11-vpc"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.lab.id
  cidr_block        = cidrsubnet(aws_vpc.lab.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.az.names[count.index]

  tags = {
    Name = "lab11-private-${count.index}"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.lab.id

  tags = {
    Name = "lab11-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Las Lambdas no tienen internet: llegan a DynamoDB por un endpoint gateway (gratuito).
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.lab.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  tags = {
    Name = "lab11-dynamodb-endpoint"
  }
}

resource "aws_security_group" "lambda" {
  name        = "lab11-lambda-sg"
  description = "SG de las Lambdas del Lab 11"
  vpc_id      = aws_vpc.lab.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Solo las Lambdas pueden hablar con el cache (puerto 6379).
resource "aws_security_group" "cache" {
  name        = "lab11-cache-sg"
  description = "SG del cluster de ElastiCache"
  vpc_id      = aws_vpc.lab.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }
}
