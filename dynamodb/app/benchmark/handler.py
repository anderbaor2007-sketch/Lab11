import os
import json
import time
import random
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def percentil(latencias, p):
    latencias_sorted = sorted(latencias)
    idx = int(len(latencias_sorted) * p / 100)
    idx = min(idx, len(latencias_sorted) - 1)
    return round(latencias_sorted[idx], 3)


def main(event, context):
    """
    Ejecuta N lecturas de última posición y devuelve p50, p95, p99.
    """
    n = event.get("n", 1000)
    num_equipos = event.get("num_equipos", 1000)
    descartar = event.get("descartar", 100)  # primeras lecturas a descartar (calentamiento)

    latencias = []
    errores = 0

    for i in range(n + descartar):
        equipo_id = f"EQ-{random.randint(1, num_equipos):04d}"
        try:
            t0 = time.perf_counter()
            table.query(
                KeyConditionExpression=Key("equipoId").eq(equipo_id),
                ScanIndexForward=False,
                Limit=1,
            )
            latencia = (time.perf_counter() - t0) * 1000  # en ms
            if i >= descartar:
                latencias.append(latencia)
        except Exception:
            errores += 1

    resultado = {
        "servicio": "dynamodb",
        "lecturas": len(latencias),
        "descartadas": descartar,
        "errores": errores,
        "p50_ms": percentil(latencias, 50),
        "p95_ms": percentil(latencias, 95),
        "p99_ms": percentil(latencias, 99),
        "promedio_ms": round(sum(latencias) / len(latencias), 3) if latencias else 0,
        "timestamp": int(time.time()),
    }

    return {
        "statusCode": 200,
        "body": json.dumps(resultado, cls=DecimalEncoder),
    }